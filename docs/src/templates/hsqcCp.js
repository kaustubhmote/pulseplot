export const hsqcCp = {
  "settings": {
    "title": "HSQC-solids",
    "figureWidth": 10,
    "figureHeight": 4.5,
    "timeRange": 12,
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
      "shape": "tan_-50_0.1",
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
      "amplitude": 0.17,
      "phase": "_decoupling",
      "text": "",
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
      "id": "el-msn15lxe-od9h5",
      "type": "pulse",
      "channel": "ch-c",
      "start": 4.5,
      "duration": 0.25,
      "amplitude": 0.85,
      "phase": "4",
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
      "id": "el-msn15ov9-i6zrt",
      "type": "pulse",
      "channel": "ch-c",
      "start": 7,
      "duration": 0.25,
      "amplitude": 0.85,
      "phase": "5",
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
      "id": "el-msn15sbg-stzze",
      "type": "pulse",
      "channel": "ch-h",
      "start": 4.75,
      "duration": 2.25,
      "amplitude": 0.17,
      "phase": "_water suppression",
      "text": "",
      "shape": "",
      "facecolor": "#14ffb9",
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
    },
    {
      "id": "el-msn169yo-9tqy7",
      "type": "pulse",
      "channel": "ch-c",
      "start": 7.25,
      "duration": 2,
      "amplitude": 0.62,
      "phase": "6",
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
      "id": "el-msn16dzk-cewge",
      "type": "shaped",
      "channel": "ch-h",
      "start": 7.25,
      "duration": 2,
      "amplitude": 0.57,
      "phase": "7",
      "text": "CP",
      "shape": "tan_50_0.1",
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
      "id": "el-msn16ltm-p6pai",
      "type": "fid",
      "channel": "ch-h",
      "start": 9.25,
      "duration": 2.5,
      "amplitude": 0.55,
      "phase": "rec",
      "text": "",
      "shape": "fid_15_5",
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
    },
    {
      "id": "el-msn17ns6-shzty",
      "type": "delay",
      "channel": "ch-c",
      "start": 2.5,
      "duration": 2,
      "amplitude": 0.45,
      "phase": "",
      "text": "t$_1$",
      "shape": "",
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
    },
    {
      "id": "el-msn1akgq-a9c1y",
      "type": "pulse",
      "channel": "ch-c",
      "start": 9.25,
      "duration": 2.5,
      "amplitude": 0.17,
      "phase": "_decoupling",
      "text": "",
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
    }
  ],
  "selectedId": "el-msn17ns6-shzty",
  "activeChannelId": "ch-c"
};
