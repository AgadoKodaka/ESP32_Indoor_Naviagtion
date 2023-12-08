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

// Function declaration
void wifi_scan(void);

/* STA Configuration */
#define SSID CONFIG_WIFI_SSID
#define PASSWORD CONFIG_WIFI_PASSWORD
#define WIFI_SCAN_INTERVAL CONFIG_WIFI_SCAN_INTERVAL
// #define MAXIMUM_RETRY CONFIG_ESP_MAXIMUM_STA_RETRY

/* The event group allows multiple bits for each event, but we only care about two events:
 * - we are connected to the AP with an IP
 * - we failed to connect after the maximum amount of retries */
// #define WIFI_CONNECTED_BIT BIT0
// #define WIFI_FAIL_BIT BIT1
// This is for Taskhanler
static const char *TAG_STA = "WiFi STA";
static const char *TAG_AP = "WiFi AP";

// Taskhanler
TaskHandle_t wifiScanTask_handler = NULL;

// static int s_retry_num = 0;

/* FreeRTOS event group to signal when we are connected/disconnected */
// static EventGroupHandle_t s_wifi_event_group;
// Start for nvs (non-volatile-storge)
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
static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data)
{
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START)
    {
        esp_wifi_connect();
        ESP_LOGI(TAG_STA, "Trying to connect with Wi-Fi\n");
    }
    else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_CONNECTED)
    {
        ESP_LOGI(TAG_STA, "Wi-Fi connected AP SSID:%s password:%s\n", SSID, PASSWORD);
    }
    else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP)
    {
        ESP_LOGI(TAG_STA, "Got AP's IP: starting MQTT Client\n");
        wifi_scan();
    }
    else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED)
    {
        ESP_LOGI(TAG_STA, "Disconnected: Retrying Wi-Fi connect to AP SSID:%s password:%s", SSID, PASSWORD);
        esp_wifi_connect();
    }
}
void wifi_int_STA(void)
{
    /* First, report to console, start STA mode
     * Second, initialize Wi-Fi network interface
     * Third, initialize eventloop for handling Wi-Fi cases
     *
     */
    ESP_LOGI(TAG_STA, "WIFI initializing STA");
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
    ESP_LOGI(TAG_STA, "WIFI initialize STA finished.");
};
void wifi_scan(void)
{
    ESP_LOGI(TAG_AP, "Starting WiFi scan...");
    while (1)
    {

        ESP_LOGI(TAG_AP, "Free memory: %d bytes", esp_get_free_heap_size());
        esp_wifi_scan_start(NULL, true);
        vTaskDelay(1000 / portTICK_PERIOD_MS); // Wait for the scan to complete

        uint16_t ap_count = 0;
        esp_wifi_scan_get_ap_num(&ap_count);

        if (ap_count == 0)
        {
            ESP_LOGI(TAG_AP, "No WiFi networks found.");
        }
        else
        {
            ESP_LOGI(TAG_AP, "Number of WiFi networks found: %u", ap_count);

            wifi_ap_record_t *ap_list = (wifi_ap_record_t *)malloc(sizeof(wifi_ap_record_t) * ap_count);
            if (ap_list)
            {
                esp_wifi_scan_get_ap_records(&ap_count, ap_list);

                for (int i = 0; i < ap_count; i++)
                {
                    ESP_LOGI(TAG_AP, "SSID: %s, RSSI: %d, Channel: %d", (char *)ap_list[i].ssid, ap_list[i].rssi, ap_list[i].primary);
                }

                free(ap_list);
            }
            else
            {
                ESP_LOGE(TAG_AP, "Failed to allocate memory for AP list.");
            }
        }

        // vTaskDelay((WIFI_SCAN_INTERVAL - 1000) / portTICK_PERIOD_MS); // Wait before the next scan
    }
}
void app_main(void)
{
    // Allow other core to finish initialization
    vTaskDelay(pdMS_TO_TICKS(200));

    // Initialize nvs partition
    ESP_LOGI(__func__, "Initialize nvs partition.");
    initialize_nvs();
    // Wait a second for memory initialization
    vTaskDelay(1000 / portTICK_RATE_MS);

    // Initialize Wi-Fi
    wifi_int_STA();
}
