#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "freertos/semphr.h"

#include "esp_mac.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif_net_stack.h"
#include "esp_netif.h"
#include "nvs_flash.h"
#include "lwip/inet.h"
#include "lwip/netdb.h"
#include "lwip/sockets.h"

#include "mqtt_client.h"

/* STA Configuration */
#define SSID CONFIG_WIFI_SSID
#define PASSWORD CONFIG_WIFI_PASSWORD
#define WIFI_SCAN_INTERVAL CONFIG_WIFI_SCAN_INTERVAL
// #define MAXIMUM_RETRY CONFIG_ESP_MAXIMUM_STA_RETRY

/* The event group allows declaring status for event
Here, we declare event connected/disconnected to AP as 1 bit:*/
static EventGroupHandle_t event_group;
const int WIFI_CONNECTED_BIT = BIT0;
const int MQTT_CONNECTED_BIT = BIT1;

static const char *TAG_CONNECT = "WiFi Connect";
static const char *TAG_SCAN = "WiFi Scan";
// static const char *TAG_LOCALIZE = "LOCALIZATION";
static const char *TAG_MQTT = "MQTT";

char *RSSI_TOPIC = NULL;
char *rssi_data_json = NULL;

esp_mqtt_client_handle_t client;

/*Targeted SSIDs*/
const char *target_ssids[] = {"STATION 1", "SSID2", "SSID3"};
const size_t num_ssids = sizeof(target_ssids) / sizeof(target_ssids[0]);

///////////////////////////// Function declaration
static void initialize_nvs(void);
static void wifi_init_STA(void);
static void mqtt_app_start(void);
static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data);
static void mqtt_event_handler(void *handler_args, esp_event_base_t base,
                               int32_t event_id, void *event_data);
void wifi_scan_task(void);

static void log_error_if_nonzero(const char *message, int error_code)
{
    if (error_code != 0)
    {
        ESP_LOGE(__func__, "Last error %s: 0x%x", message, error_code);
    }
}
///////////////////////////// Initialization functions
/* Start for non - voltail storge (where ESP32 will store the data)*/
static void initialize_nvs(void)
{
    esp_err_t error = nvs_flash_init();
    if (error == ESP_ERR_NVS_NO_FREE_PAGES || error == ESP_ERR_NVS_NEW_VERSION_FOUND)
    {
        ESP_ERROR_CHECK_WITHOUT_ABORT(nvs_flash_erase());
        error = nvs_flash_init();
    }
    ESP_ERROR_CHECK_WITHOUT_ABORT(error);
}

static void wifi_init_STA(void)
{
    /* First, report to console, start STA mode
     * Second, initialize Wi-Fi network interface
     * Third, initialize eventloop for handling Wi-Fi cases
     *
     */
    ESP_LOGI(TAG_CONNECT, "WIFI initializing STA mode");
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_netif_init());
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();

    // Event Handler
    ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &wifi_event_handler,
                                                        NULL,
                                                        NULL));
    ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT,
                                                        ESP_EVENT_ANY_ID,
                                                        &wifi_event_handler,
                                                        NULL,
                                                        NULL));

    wifi_init_config_t WIFI_initConfig = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_init(&WIFI_initConfig));

    static wifi_config_t wifi_config = {
        .sta = {
            .ssid = SSID,
            .password = PASSWORD,
            .threshold.authmode = WIFI_AUTH_WPA2_PSK,
            .pmf_cfg = {
                .capable = true,
                .required = false,
            },
        },
    };
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK_WITHOUT_ABORT(esp_wifi_start());
    ESP_LOGI(TAG_CONNECT, "WIFI initialize STA mode finished.");
};

static void mqtt_app_start(void)
{
    esp_mqtt_client_config_t mqtt_cfg = {
        .uri = CONFIG_BROKER_URL,
        // .event_handle = mqtt_event_handler,
    };

    client = esp_mqtt_client_init(&mqtt_cfg);
    esp_mqtt_client_register_event(client, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);
    esp_mqtt_client_start(client);
}

///////////////////////////// Event handler functions

static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data)
{
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START)
    {
        esp_wifi_connect();
        ESP_LOGI(TAG_CONNECT, "Trying to connect with Wi-Fi\n");
    }
    else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_CONNECTED)
    {
        ESP_LOGI(TAG_CONNECT, "Wi-Fi connected AP SSID:%s password:%s\n", SSID, PASSWORD);
    }
    else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP)
    {
        xEventGroupSetBits(event_group, WIFI_CONNECTED_BIT);
        ESP_LOGI(TAG_CONNECT, "Got AP's IP: MQTT can be connected");
        mqtt_app_start();
    }
    else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED)
    {
        xEventGroupClearBits(event_group, WIFI_CONNECTED_BIT);
        ESP_LOGI(TAG_CONNECT, "Disconnected: WiFi Scan paused");
        esp_wifi_connect();
    }
}

//////////////////////////////////////////////////
//! TODO: Fix MQTT event handler function
//////////////////////////////////////////////////
static void mqtt_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data)
{
    esp_mqtt_event_handle_t event = event_data;
    // esp_mqtt_client_handle_t client = event->client;
    // int msg_id;
    switch ((esp_mqtt_event_id_t)event_id)
    {
    case MQTT_EVENT_CONNECTED:
        ESP_LOGI(TAG_MQTT, "MQTT_EVENT_CONNECTED");
        xEventGroupSetBits(event_group, MQTT_CONNECTED_BIT);
        break;
    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGI(TAG_MQTT, "MQTT_EVENT_DISCONNECTED");
        xEventGroupClearBits(event_group, MQTT_CONNECTED_BIT);
        break;

    case MQTT_EVENT_SUBSCRIBED:
        ESP_LOGI(TAG_MQTT, "MQTT_EVENT_SUBSCRIBED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_UNSUBSCRIBED:
        ESP_LOGI(TAG_MQTT, "MQTT_EVENT_UNSUBSCRIBED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_PUBLISHED:
        ESP_LOGI(TAG_MQTT, "MQTT_EVENT_PUBLISHED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_DATA:
        ESP_LOGI(TAG_MQTT, "MQTT_EVENT_DATA");
        printf("TOPIC=%.*s\r\n", event->topic_len, event->topic);
        printf("DATA=%.*s\r\n", event->data_len, event->data);
        break;
    case MQTT_EVENT_ERROR:
        ESP_LOGI(TAG_MQTT, "MQTT_EVENT_ERROR");
        if (event->error_handle->error_type == MQTT_ERROR_TYPE_TCP_TRANSPORT)
        {
            log_error_if_nonzero("reported from esp-tls", event->error_handle->esp_tls_last_esp_err);
            log_error_if_nonzero("reported from tls stack", event->error_handle->esp_tls_stack_err);
            log_error_if_nonzero("captured as transport's socket errno", event->error_handle->esp_transport_sock_errno);
            ESP_LOGI(TAG_MQTT, "Last errno string (%s)", strerror(event->error_handle->esp_transport_sock_errno));
        }
        break;
    default:
        ESP_LOGI(TAG_MQTT, "Other event id:%d", event->event_id);
        break;
    }
}

///////////////////////////// Task functions
void wifi_scan_task(void)
{
    ESP_LOGI(TAG_SCAN, "Starting WiFi scan...");
    while (1)
    {
        // Wait for the connected bit to be set
        xEventGroupWaitBits(event_group, WIFI_CONNECTED_BIT, pdFALSE, pdTRUE, portMAX_DELAY);
        xEventGroupWaitBits(event_group, MQTT_CONNECTED_BIT, pdFALSE, pdTRUE, portMAX_DELAY);

        ESP_LOGI(TAG_SCAN, "Both WiFi and MQTT are connected. Proceeding to scan for Wifi");
        ESP_LOGI(TAG_SCAN, "Scanning for WiFi networks...");
        ESP_LOGI(TAG_SCAN, "Free memory: %d bytes", esp_get_free_heap_size());

        for (size_t i = 0; i < num_ssids; i++)
        {
            ESP_LOGI(TAG_SCAN, "Scanning for SSID: %s", target_ssids[i]);
            wifi_scan_config_t scan_config = {
                .ssid = (uint8_t *)target_ssids[i],
                .bssid = 0,
                .channel = 1,
                .show_hidden = true};
            esp_wifi_scan_start(&scan_config, true);
            // vTaskDelay(1000 / portTICK_PERIOD_MS); // Wait for the scan to complete

            uint16_t ap_count = 0;
            esp_wifi_scan_get_ap_num(&ap_count);

            if (ap_count == 0)
            {
                ESP_LOGI(TAG_SCAN, "No WiFi networks found.");
            }
            else
            {
                ESP_LOGI(TAG_SCAN, "Number of WiFi networks found: %u", ap_count);

                wifi_ap_record_t *ap_list = (wifi_ap_record_t *)malloc(sizeof(wifi_ap_record_t) * ap_count);
                if (ap_list)
                {
                    esp_wifi_scan_get_ap_records(&ap_count, ap_list);

                    for (int i = 0; i < ap_count; i++)
                    {
                        ESP_LOGI(TAG_SCAN, "SSID: %s, RSSI: %d, Channel: %d", (char *)ap_list[i].ssid, ap_list[i].rssi, ap_list[i].primary);

                        /* Create Json string for publishing*/
                        sprintf(RSSI_TOPIC, "/rssi/%s", (char *)ap_list[i].ssid);
                        sprintf(rssi_data_json, "{'SSID':'%s','RSSI': %d,'Channel': %d}\n",
                                (char *)ap_list[i].ssid, ap_list[i].rssi, ap_list[i].primary);
                        ESP_LOGI(TAG_MQTT, "RSSI_TOPIC:[%s]", RSSI_TOPIC);
                        printf(rssi_data_json);

                        esp_mqtt_client_publish(client, RSSI_TOPIC, rssi_data_json, 0, 1, 0);
                    }

                    free(ap_list);
                }
                else
                {
                    ESP_LOGE(TAG_SCAN, "Failed to allocate memory for AP list.");
                }
            }
            // Check if disconnected before delaying for next scan
            vTaskDelay(200 / portTICK_PERIOD_MS); // Wait for the scan to complete
            if (!(xEventGroupGetBits(event_group) & WIFI_CONNECTED_BIT))
            {
                ESP_LOGI(TAG_SCAN, "WiFi Disconnected: Scan Paused");
                continue; // Immediately check connection status again
            }
            vTaskDelay(500 / portTICK_PERIOD_MS); // Wait before the next scan
        }
    }
}

void app_main(void)
{
    ESP_LOGI(TAG_MQTT, "[APP] Startup..");
    ESP_LOGI(TAG_MQTT, "[APP] Free memory: %d bytes", esp_get_free_heap_size());
    ESP_LOGI(TAG_MQTT, "[APP] IDF version: %s", esp_get_idf_version());

    esp_log_level_set("*", ESP_LOG_INFO);
    esp_log_level_set("MQTT_CLIENT", ESP_LOG_VERBOSE);
    esp_log_level_set("TRANSPORT_TCP", ESP_LOG_VERBOSE);
    esp_log_level_set("TRANSPORT_SSL", ESP_LOG_VERBOSE);
    esp_log_level_set("TRANSPORT", ESP_LOG_VERBOSE);
    // esp_log_level_set("OUTBOX", ESP_LOG_VERBOSE);

    // Initialize dynamic variables
    RSSI_TOPIC = (char *)malloc(50 * sizeof(char));
    rssi_data_json = (char *)malloc(200 * sizeof(char));

    // Allow other core to finish initialization
    vTaskDelay(pdMS_TO_TICKS(200));

    // Initialize nvs partition
    ESP_LOGI(__func__, "Initialize nvs partition.");
    initialize_nvs();
    // Wait a second for memory initialization
    vTaskDelay(1000 / portTICK_RATE_MS);

    // Initialize event group
    event_group = xEventGroupCreate();

    // Initialize Wi-Fi
    ESP_LOGI(__func__, "Initialize Wifi STA mode");
    wifi_init_STA();
    // Wait a second for Wi-Fi initialization
    vTaskDelay(1000 / portTICK_RATE_MS);

    // Initialize MQTT
    // ESP_LOGI(__func__, "Initialize MQTT client");
    // mqtt_app_start();

    // Create a Wi-Fi scan task
    xTaskCreate(&wifi_scan_task, "wifi_scan_task", 4096, NULL, 5, NULL);
}
