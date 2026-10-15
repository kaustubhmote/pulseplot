export const crossPolarization = {
  "settings": {
    "title": "Cross-Polarization (CP-MAS)",
    "figureWidth": 10,
    "figureHeight": 4.5,
    "timeRange": 8,
    "snap": 0.25,
    "channelSpacing": 132,
    "fontSize": 14,
    "grid": true,
    "labels": true,
    "theme": "light"
  },
  "channels": [
    {
      "id": "ch-h",
      "name": "¹H",
      "value": 1.5
    },
    {
      "id": "ch-c",
      "name": "¹³C",
      "value": 0
    }
  ],
  "elements": [
    {
      "id": "el-msn0famu-eni5z",
      "type": "pulse",
      "channel": "ch-h",
      "start": 0.25,
      "duration": 0.25,
      "amplitude": 0.85,
      "phase": "1",
      "text": "",
      "shape": "",
      "facecolor": "#000000",
      "edgecolor": "#000000",
      "textcolor": "#000000",
      "truncateOff": false,
      "tdx": 0,
      "tdy": -0.3,
      "tfs": 14,
      "pdx": 0,
      "pdy": 0,
      "pfs": 14,
      "allowOverlap": true,
      "rotorInsetWidth": 1.5,
      "rotorYOffset": 0.5,
      "customPoints": [
        [
          0,
          0
        ],
        [
          0.2,
          0.3
        ],
        [
          0.5,
          1
        ],
        [
          0.8,
          0.3
        ],
        [
          1,
          0
        ]
      ]
    },
    {
      "id": "el-msn0famu-8wg36",
      "type": "shaped",
      "channel": "ch-h",
      "start": 0.5,
      "duration": 2,
      "amplitude": 0.57,
      "phase": "2",
      "text": "CP",
      "shape": "ramp_50",
      "facecolor": "#ffffff",
      "edgecolor": "#000000",
      "textcolor": "#000000",
      "truncateOff": false,
      "tdx": 0,
      "tdy": -0.4,
      "tfs": 14,
      "pdx": 0,
      "pdy": 0,
      "pfs": 14,
      "allowOverlap": true,
      "rotorInsetWidth": 1.5,
      "rotorYOffset": 0.5,
      "customPoints": [
        [
          0,
          0
        ],
        [
          0.2,
          0.3
        ],
        [
          0.5,
          1
        ],
        [
          0.8,
          0.3
        ],
        [
          1,
          0
        ]
      ]
    },
    {
      "id": "el-msn0famu-bi1zb",
      "type": "pulse",
      "channel": "ch-c",
      "start": 0.5,
      "duration": 2,
      "amplitude": 0.62,
      "phase": "3",
      "text": "CP",
      "shape": "",
      "facecolor": "#ffffff",
      "edgecolor": "#000000",
      "textcolor": "#000000",
      "truncateOff": false,
      "tdx": 0,
      "tdy": -0.3,
      "tfs": 14,
      "pdx": 0,
      "pdy": 0,
      "pfs": 14,
      "allowOverlap": true,
      "rotorInsetWidth": 1.5,
      "rotorYOffset": 0.5,
      "customPoints": [
        [
          0,
          0
        ],
        [
          0.2,
          0.3
        ],
        [
          0.5,
          1
        ],
        [
          0.8,
          0.3
        ],
        [
          1,
          0
        ]
      ]
    },
    {
      "id": "el-msn0famu-xrd4z",
      "type": "pulse",
      "channel": "ch-h",
      "start": 2.5,
      "duration": 2.25,
      "amplitude": 0.84,
      "phase": "",
      "text": "decoupling",
      "shape": "",
      "facecolor": "#ffffff",
      "edgecolor": "#000000",
      "textcolor": "#000000",
      "truncateOff": false,
      "tdx": 0,
      "tdy": -0.3,
      "tfs": 14,
      "pdx": 0,
      "pdy": 0,
      "pfs": 14,
      "allowOverlap": true,
      "rotorInsetWidth": 1.5,
      "rotorYOffset": 0.5,
      "customPoints": [
        [
          0,
          0
        ],
        [
          0.2,
          0.3
        ],
        [
          0.5,
          1
        ],
        [
          0.8,
          0.3
        ],
        [
          1,
          0
        ]
      ]
    },
    {
      "id": "el-msn0famu-8j764",
      "type": "shaped",
      "channel": "ch-c",
      "start": 2.5,
      "duration": 2.25,
      "amplitude": 0.55,
      "phase": "rec",
      "text": "",
      "shape": "fid_15_3",
      "facecolor": "#ffffff",
      "edgecolor": "#000000",
      "textcolor": "#000000",
      "truncateOff": false,
      "tdx": 0,
      "tdy": 0,
      "tfs": 14,
      "pdx": 0,
      "pdy": 0,
      "pfs": 14,
      "allowOverlap": true,
      "rotorInsetWidth": 1.5,
      "rotorYOffset": 0.5,
      "customPoints": [
        [
          0,
          0
        ],
        [
          0.2,
          0.3
        ],
        [
          0.5,
          1
        ],
        [
          0.8,
          0.3
        ],
        [
          1,
          0
        ]
      ]
    }
  ],
  "selectedId": null,
  "activeChannelId": "ch-h"
};
