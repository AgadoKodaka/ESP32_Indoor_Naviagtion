import React, { useState, useEffect, useRef } from "react";
import mqtt from "precompiled-mqtt";
import mapImage from "../images/RoomMap.png"; // Ensure this is the path to your map image file

import "./MapPage.css";

const MapPage = () => {
  const [deviceIdInput, setDeviceIdInput] = useState(""); // This is the input value for the device ID form
  const [deviceId, setDeviceId] = useState("");
  const [currentLocation, setCurrentLocation] = useState([ 100, 260 ]);
  const [selectedRoom, setSelectedRoom] = useState("");
  const [pathCoordinates, setPathCoordinates] = useState([]);
  const canvasRef = useRef(null);
  const mqttClientRef = useRef(null);

  // Room coordinates
  const roomCoordinates = {
    401: [480, 360],
    402: [480, 240],
    403: [360, 480],
    404: [360, 240],
    405: [240, 360],
    406: [240, 240],
    // Add the rest of the rooms with their fixed coordinates
  };

  // Define the trackable points on the map and their neighboring points
  const trackPointsWithNeighbors = {
    "120,120": [
      [240, 120],
      [120, 240],
    ],
    "240,120": [
      [120, 120],
      [360, 120],
      [240, 240],
    ],
    "360,120": [
      [240, 120],
      [480, 120],
      [360, 240],
    ],
    "480,120": [
      [360, 120],
      [480, 240],
    ],

    "120,240": [
      [120, 120],
      [120, 360],
    ],
    "240,240": [
      [240, 120],
      [240, 360],
    ],
    "360,240": [
      [360, 120],
      [360, 360],
    ],
    "480,240": [
      [480, 120],
      [480, 360],
    ],

    "120,360": [
      [120, 480],
      [120, 240],
    ],
    "240,360": [
      [240, 480],
      [240, 240],
      [360, 360],
    ],
    "360,360": [
      [360, 480],
      [360, 240],
      [240, 360],
    ],
    "480,360": [
      [480, 480],
      [480, 240],
    ],

    "120,480": [
      [120, 360],
      [240, 480],
    ],
    "240,480": [
      [240, 360],
      [120, 480],
    ],
    "360,480": [
      [360, 360],
      [480, 480],
    ],
    "480,480": [
      [360, 480],
      [480, 360],
    ],
  };

  // MQTT connection setup
  useEffect(() => {
    if (deviceId) {
      // Only connect to MQTT if deviceId is set
      mqttClientRef.current = mqtt.connect("mqtt://test.mosquitto.org:8081"); // Use your MQTT broker URL

      mqttClientRef.current.on("connect", () => {
        console.log(`Connected to MQTT broker as device ${deviceId}`);
        mqttClientRef.current.subscribe(`${deviceId}/location`, (err) => {
          if (!err) {
            console.log(`Subscribed to topic ${deviceId}/location`);
          }
        });
      });

      mqttClientRef.current.on("message", (topic, message) => {
        // Parse message and update current location state
        const location = JSON.parse(message.toString());
        let convertedLocation = [location.posX, location.posY]
        setCurrentLocation(convertedLocation);
      });

      const interval = setInterval(() => {
        // This interval does nothing for now, but you can use it if needed
      }, 3000);

      return () => {
        clearInterval(interval);
        if (mqttClientRef.current) {
          mqttClientRef.current.end();
        }
      };
    }
  }, [deviceId]);

  ////////////////////////////////////////////
  // Handling form submission
  const handleDeviceIdSubmit = (e) => {
    e.preventDefault();
    // Here, you can add additional logic before setting the deviceId
    setDeviceId(deviceIdInput);
  };

  const handleRoomSelectionSubmit = (e) => {
    e.preventDefault();
    if (selectedRoom) {
      const end = roomCoordinates[selectedRoom];
      console.log("request navigation");
      console.log("start point (current location): ", currentLocation);
      console.log("end: ", end);
      const path = findPath(currentLocation, end, trackPointsWithNeighbors);
      console.log("Found path:");
      console.log(path);
      setPathCoordinates(path);
    }
  };

  ////////////////////////////////////////////
  // Path calculation
  ////////////////////////////////////////////

  const findPath = (currentLocation, end, trackPointsWithNeighbors) => {
    // Helper function to calculate the distance between points (heuristic)
    const distance = (point1, point2) => {
      return Math.abs(point1[0] - point2[0]) + Math.abs(point1[1] - point2[1]);
    };
    // Helper function to find the nearest point to the current location
    const findNearestTrackPoint = (currentLocation, trackPointsWithNeighbors) => {
      let nearestPoint = null;
      let smallestDistance = Infinity;

      Object.keys(trackPointsWithNeighbors).forEach(key => {
        const [x, y] = key.split(',').map(Number);
        const distanceToCurrent = Math.sqrt(
          Math.pow(x - currentLocation[0], 2) + Math.pow(y - currentLocation[1], 2)
        );
        if (distanceToCurrent < smallestDistance) {
          smallestDistance = distanceToCurrent;
          nearestPoint = [x, y];
        }
      });

      return nearestPoint;
    };

    // Convert currentLocation to the nearest trackable point
    const start = findNearestTrackPoint(currentLocation, trackPointsWithNeighbors);

    // Initialize open and closed list
    let openList = [];
    let closedList = [];

    // Start by adding the start point to the open list
    openList.push({
      coord: start,
      g: 0,
      h: distance(start, end),
      f: 0,
      parent: null,
    });

    while (openList.length > 0) {
      // Get the node with the least f value
      let currentPoint = openList.reduce((prev, curr) =>
        prev.f < curr.f ? prev : curr
      );

      // End case -- result has been found, return the traced path
      if (
        currentPoint.coord[0] === end[0] &&
        currentPoint.coord[1] === end[1]
      ) {
        let curr = currentPoint;
        let path = [];
        while (curr) {
          path.push(curr.coord);
          curr = curr.parent;
        }

        // Reverse to get the path from start to end
        path = path.reverse();

        // Add the actual current location to the beginning of the path
        path.unshift(currentLocation);
        return path;
      }

      // Remove the current point from the open list
      openList = openList.filter((point) => point !== currentPoint);

      // Add it to the closed list
      closedList.push(currentPoint);

      // Generate children points (neighbors)
      let coordKey = currentPoint.coord[0] + "," + currentPoint.coord[1];
      let neighbors = trackPointsWithNeighbors[coordKey] || [];
      neighbors = neighbors.filter((neighborCoord) => {
        return !closedList.some(
          (closedPoint) =>
            closedPoint.coord[0] === neighborCoord[0] &&
            closedPoint.coord[1] === neighborCoord[1]
        );
      });

      // Loop through children
      for (let neighborCoord of neighbors) {
        const neighbor = { coord: neighborCoord };

        // Child is already on the closed list
        if (
          closedList.find(
            (point) =>
              point.coord[0] === neighborCoord[0] &&
              point.coord[1] === neighborCoord[1]
          )
        ) {
          continue;
        }

        // Create the f, g, and h values
        neighbor.g = currentPoint.g + 1;
        neighbor.h = distance(neighborCoord, end);
        neighbor.f = neighbor.g + neighbor.h;
        neighbor.parent = currentPoint;

        // Child is already in the open list
        if (
          openList.some(
            (point) =>
              point.coord[0] === neighborCoord[0] &&
              point.coord[1] === neighborCoord[1] &&
              neighbor.g > point.g
          )
        ) {
          continue;
        }

        // Add the child to the open list
        openList.push(neighbor);
      }
    }

    // No path found
    return [];
  };

  // Canvas drawing logic
  useEffect(() => {
    console.log("Drawing canvas deviceId dependencies");
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext("2d");
      // Your canvas drawing code here
      const image = new Image();

      image.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
      };

      image.src = mapImage;
    }
  }, [deviceId]);

  //Draw canvas when current location or navigated path changes
  useEffect(() => {
    console.log(
      "Drawing canvas currentLocation or pathCoordinates dependencies"
    );
    console.log(currentLocation);
    console.log(pathCoordinates);
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext("2d");
      const image = new Image();

      image.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        // Reset the axis transformation to draw image normally
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
        
        // Transform the axis to draw current location and path
        ctx.translate(canvas.width, canvas.height); // Move the origin to the bottom-right corner        
        ctx.scale(-1, -1); // Flip the both axis
        // Draw current location
        ctx.fillStyle = "red";
        ctx.beginPath();
        ctx.arc(currentLocation[0], currentLocation[1], 10, 0, 2 * Math.PI);
        ctx.fill();

        // Draw path if it exists
        if (pathCoordinates.length > 0) {
          ctx.strokeStyle = "blue";
          ctx.lineWidth = 5;
          ctx.beginPath();
          ctx.moveTo(pathCoordinates[0][0], pathCoordinates[0][1]);
          pathCoordinates.forEach((point) => {
            ctx.lineTo(point[0], point[1]);
          });
          ctx.stroke();
        }
      };
      image.src = mapImage;
    }
  }, [currentLocation, pathCoordinates]);

  return (
    <div className="container">
      <div>
        <h1>Welcome to the Hospital Navigation System</h1>
        <form onSubmit={handleDeviceIdSubmit}>
          <label>
            Device ID:
            <input
              type="text"
              value={deviceIdInput}
              onChange={(e) => setDeviceIdInput(e.target.value)}
              required
            />
          </label>
          <button type="submit">Submit</button>
        </form>
      </div>
      {deviceId ? (
        // Map and room selection form
        <div>
          <h1>Map</h1>
          <form onSubmit={handleRoomSelectionSubmit}>
            <label>
              Room Number:
              <select
                value={selectedRoom}
                onChange={(e) => setSelectedRoom(e.target.value)}
                required
              >
                <option value="">Select a room...</option>
                {Object.keys(roomCoordinates).map((roomNumber) => (
                  <option key={roomNumber} value={roomNumber}>
                    {roomNumber}
                  </option>
                ))}
              </select>
            </label>
            <button type="submit">Navigate</button>
          </form>
          <canvas ref={canvasRef} width={600} height={600} />
        </div>
      ) : (
        <div></div>
      )}
    </div>
  );
};

export default MapPage;
