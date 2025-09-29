// Static transit configuration for offline operation
// Auto-generated from backend data - DO NOT EDIT MANUALLY
// Last updated: 2025-09-28T23:16:00Z

export const transitConfig = {
  lastUpdated: "2025-09-28T23:16:00Z",
  version: "1.0.0",

  stations: [
    { id: 1, name: "Central Station" },
    { id: 2, name: "Union Square" },
    { id: 3, name: "Airport Terminal" },
    { id: 4, name: "Downtown" },
    { id: 5, name: "University" },
    { id: 6, name: "Stadium" },
    { id: 7, name: "Harbor Point" },
    { id: 8, name: "Tech Center" }
  ],

  pricing: [
    { stationA: 1, stationB: 2, fare: 3.25 },
    { stationA: 1, stationB: 3, fare: 4.5 },
    { stationA: 1, stationB: 4, fare: 2.75 },
    { stationA: 1, stationB: 5, fare: 5.0 },
    { stationA: 1, stationB: 6, fare: 3.75 },
    { stationA: 1, stationB: 7, fare: 4.25 },
    { stationA: 1, stationB: 8, fare: 3.5 },
    { stationA: 2, stationB: 3, fare: 4.0 },
    { stationA: 2, stationB: 4, fare: 2.5 },
    { stationA: 2, stationB: 5, fare: 5.5 },
    { stationA: 2, stationB: 6, fare: 3.0 },
    { stationA: 2, stationB: 7, fare: 4.75 },
    { stationA: 2, stationB: 8, fare: 3.25 },
    { stationA: 3, stationB: 4, fare: 2.25 },
    { stationA: 3, stationB: 5, fare: 4.5 },
    { stationA: 3, stationB: 6, fare: 3.75 },
    { stationA: 3, stationB: 7, fare: 5.25 },
    { stationA: 3, stationB: 8, fare: 2.75 },
    { stationA: 4, stationB: 5, fare: 4.0 },
    { stationA: 4, stationB: 6, fare: 3.5 },
    { stationA: 4, stationB: 7, fare: 4.25 },
    { stationA: 4, stationB: 8, fare: 2.5 },
    { stationA: 5, stationB: 6, fare: 5.0 },
    { stationA: 5, stationB: 7, fare: 3.25 },
    { stationA: 5, stationB: 8, fare: 4.75 },
    { stationA: 6, stationB: 7, fare: 3.75 },
    { stationA: 6, stationB: 8, fare: 2.25 },
    { stationA: 7, stationB: 8, fare: 3.25 }
  ],

  minimumFare: 2.25
}