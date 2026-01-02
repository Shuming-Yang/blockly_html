'use strict';

let workspace = null;

// =============================================================
// 1. 自定義欄位 (FieldHex)
// =============================================================
class FieldHex extends Blockly.FieldTextInput {
  constructor(value, opt_validator, opt_config) {
    super(value, opt_validator, opt_config);
  }

  // 複寫驗證器，確保所有輸入都符合 Hex 格式
  doClassValidation_(newValue) {
    if (typeof newValue !== 'string') {
      return null;
    }
    // 自動轉大寫並過濾非 0-9, A-F 字元
    var cleanedValue = newValue.toUpperCase().replace(/[^0-9A-F]/g, '');
    return cleanedValue;
  }
}

// 註冊自定義欄位
Blockly.fieldRegistry.register('field_hex', FieldHex);

// =============================================================
// 2. 積木定義 (JSON)
// =============================================================
const customBlocksJson = [
  {
    "type": "SOF",
    "message0": "SOF中要做的事 %1 %2 %3",
    "args0": [
      { "type": "field_input", "name": "NAME", "text": "SOF" },
      { "type": "field_label", "name": "PARAMS", "text": "" },
      { "type": "input_dummy" }
    ],
    "message1": "%1",
    "args1": [
      { "type": "input_statement", "name": "STACK" }
    ],
    "colour": 290
  },
  {
    "type": "StartUp",
    "message0": "測試前要做的事 %1 %2 %3",
    "args0": [
      { "type": "field_input", "name": "NAME", "text": "Startup" },
      { "type": "field_label", "name": "PARAMS", "text": "" },
      { "type": "input_dummy" }
    ],
    "message1": "%1",
    "args1": [
      { "type": "input_statement", "name": "STACK" }
    ],
    "colour": 290
  },
  {
    "type": "Timer",
    "message0": "Timer中要做的事 %1 %2 %3",
    "args0": [
      { "type": "field_input", "name": "NAME", "text": "Timer" },
      { "type": "field_label", "name": "PARAMS", "text": "" },
      { "type": "input_dummy" }
    ],
    "message1": "%1",
    "args1": [
      { "type": "input_statement", "name": "STACK" }
    ],
    "colour": 290
  },
  {
    "type": "SCCB",
    "message0": "SCCB Read %1 %2 %3 %4 %5 %6",
    "args0": [
      { "type": "field_label_serializable", "name": "LB_dev_id", "text": "dev_id" },        
      { "type": "field_hex", "name": "dev_id", "text": "6C" },
      { "type": "field_label_serializable", "name": "LB_addr", "text": "addr" }, 
      { "type": "field_hex", "name": "addr", "text": "300A" },
      { "type": "field_label_serializable", "name": "LB_length", "text": "len" },        
      { "type": "field_dropdown", "name": "len_cfg", "options": [
              ['1byte', '1'], ['2bytes', '2'],['3bytes', '3'], ['4bytes', '4']] }
    ],
    "output": "String",
    "colour": 230
  },
  {
    "type": "Emb",
    "message0": "Emb Read offset %1 %2 %3 %4 %5",
    "args0": [
      { "type": "field_dropdown", "name": "emb_sel", "options": [
              ['TOP', 'top'], ['BTM', 'btm']] },
      { "type": "field_label_serializable", "name": "LB_offset", "text": "offset" }, 
      { "type": "field_input", "name": "offset", "text": "00" },
            { "type": "field_label_serializable", "name": "LB_length", "text": "len" },        
      { "type": "field_dropdown", "name": "len_cfg", "options": [
              ['1byte', '1'], ['2bytes', '2'],['3bytes', '3'], ['4bytes', '4']] }
    ],
    "output": "String",
    "colour": 230
  },
    {
    "type": "Var",
    "message0": "Var Read from %1",
    "args0": [
      { "type": "field_dropdown", "name": "var_sel", "options": [
              ['Variable0', 'var0'], ['Variable1', 'var1'],['Variable2', 'var2'], ['Variable3', 'var3'], ['Variable4', 'var4'], ['Variable5', 'var5'],
              ['Variable6', 'var6'], ['Variable7', 'var7'],['Variable8', 'var8'], ['Variable9', 'var9'], ['Variable10', 'var10'], ['Variable11', 'var11'],
              ['Variable12', 'var12'], ['Variable13', 'var13'],['Variable14', 'var14'], ['Variable15', 'var15']] }
    ],
    "output": "String",
    "colour": 230
  },
   {
    "type": "ISP",
    "message0": "Read FW/ISP %1",
    "args0": [
      { "type": "field_dropdown", "name": "isp_sel", "options": [
              ['luminance', 'luminance'], ['TICK_1ms', 'TICK_1ms'],['Err_status', 'Err_status'], ['FPS', 'FPS'], ['FPS_Min', 'FPS_Min'], ['FPS_Max', 'FPS_Max']] }
    ],
    "output": "String",
    "colour": 230
  },
  {
    "type": "MASK",
    "message0": "Mask %1 %2 %3",
    "args0": [
      { "type": "input_value", "name": "A", "check": "String" },
      { "type": "field_label_serializable", "name": "and", "text": "&" },    
      { "type": "field_hex", "name": "mask", "text": "FFFFFFFF" }
    ],
    "output": "String",
    "colour": 230
  },
  {
    "type": "ATBGPIO",
    "message0": "ATB GPIO %1 %2",
    "args0": [
      { "type": "field_dropdown", "name": "gpio_sel", "options": [
              ['GPIO0', 'gpio0'], ['GPIO1', 'gpio1']] },    
      { "type": "field_dropdown", "name": "len_cfg", "options": [
              ['Low', 'L'], ['High', 'H'], ['Pulse', 'pulse']] }
    ],
    "previousStatement": null, 
    "nextStatement": null,     
    "colour": 160,
    "tooltip": "設GPIO",
    "helpUrl": ""
  },
  {
    "type": "MCUGPIO",
    "message0": "MCU GPIO %1 %2",
    "args0": [
      { "type": "field_dropdown", "name": "gpio_sel", "options": [
              ['GPIO0', 'gpio0'], ['GPIO1', 'gpio1']] },    
      { "type": "field_dropdown", "name": "len_cfg", "options": [
              ['Low', 'L'], ['High', 'H'], ['Pulse', 'pulse']] }
    ],
    "previousStatement": null, 
    "nextStatement": null,     
    "colour": 160,
    "tooltip": "設GPIO",
    "helpUrl": ""
  },
  {
    "type": "WSCCB",
    "message0": "SCCB Write dev_id %1 addr %2 data %3",
    "args0": [
      { "type": "field_hex", "name": "dev_id", "text": "6c" },
      { "type": "field_hex", "name": "addr", "text": "0100" },
      { "type": "field_hex", "name": "data", "text": "01" }
    ],
    "previousStatement": null, 
    "nextStatement": null,     
    "colour": 160,
    "tooltip": "write device",
    "helpUrl": ""
  },
  {
    "type": "set_var",
    "message0": "set %1 from %2",
    "args0": [
      {
        "type": "field_dropdown", "name": "var_sel", "options": [
          ['Variable0', 'var0'], ['Variable1', 'var1'], ['Variable2', 'var2'], ['Variable3', 'var3'], ['Variable4', 'var4'], ['Variable5', 'var5'],
          ['Variable6', 'var6'], ['Variable7', 'var7'], ['Variable8', 'var8'], ['Variable9', 'var9'], ['Variable10', 'var10'], ['Variable11', 'var11'],
          ['Variable12', 'var12'], ['Variable13', 'var13'], ['Variable14', 'var14'], ['Variable15', 'var15']
        ]
      },
      { "type": "input_value", "name": "data", "check": "String" }
    ],
    "previousStatement": null, 
    "nextStatement": null,     
    "colour": 160,
    "tooltip": "write device",
    "helpUrl": ""
  },
  {
    "type": "TXT",
    "message0": "Run TXT file %1",
    "args0": [
      { "type": "field_input","name": "TEXT", "text": "file name" }
    ],
    "previousStatement": null, 
    "nextStatement": null,     
    "colour": 160,
    "tooltip": "執行txt中的sccb cmd",
    "helpUrl": ""
  },
  {
    "type": "compare_ex",
    "message0": "%1 %2 %3",
    "args0": [
      { "type": "input_value", "name": "A", "check": "String" },
      { "type": "field_dropdown", "name": "OP", "options": [
              ['=', 'EQ'], ['\u2260', 'NEQ'], ['<', 'LT'], 
              ['\u2264', 'LTE'], ['>', 'GT'], ['\u2265', 'GTE']] },
      { "type": "input_value", "name": "B", "check": "String" }
    ],
    "inputsInline": true,
    "output": "Boolean",
    "colour": 230,
    "tooltip": "",
    "helpUrl": ""
  },
  {
    "type": "Check_range",
    "message0": "%1 %2 %3 %4 %5",
    "args0": [
      { "type": "field_input", "name": "A", "text": "0000" },
      { "type": "field_label_serializable", "name": "LB_op1", "text": "<" },
      { "type": "input_value", "name": "input", "check": "String" },
      { "type": "field_label_serializable", "name": "LB_op2", "text": "<" },
      { "type": "field_input", "name": "B", "text": "0100" },
    ],
    "inputsInline": true,
    "output": "Boolean",
    "colour": 230,
    "tooltip": "",
    "helpUrl": ""
  }
];

// 註冊積木定義
Blockly.defineBlocksWithJsonArray(customBlocksJson);

// =============================================================
// 3. Toolbox 定義 (JSON Format)
// =============================================================
const toolbox = {
  "kind": "categoryToolbox",
  "contents": [
    {
      "kind": "category",
      "name": "Logic",
      "contents": [
        { "kind": "block", "type": "controls_if"}
      ]
    },
    {
      "kind": "category",
      "name": "Loops",
      "contents": [
        { "kind": "block", "type": "controls_repeat_ext"},
        { "kind": "block", "type": "controls_whileUntil"},
        { "kind": "block", "type": "controls_forEach" },
        { "kind": "block", "type": "controls_flow_statements" }
      ]
    },
    {
      "kind": "category",
      "name": "Math",
      "contents": [
        { "kind": "block", "type": "math_number"},
        { "kind": "block", "type": "math_arithmetic"},
        { "kind": "block", "type": "math_single" }
      ]
    },
    {
      "kind": "category",
      "name": "自訂積木區",
      "colour": "230",
      "contents": [
        { "kind": "block", "type": "SCCB" },
        { "kind": "block", "type": "Emb" },
        { "kind": "block", "type": "Var" },
        { "kind": "block", "type": "ISP" },
        { "kind": "block", "type": "MASK" },
        { "kind": "block", "type": "ATBGPIO" },
        { "kind": "block", "type": "MCUGPIO" },
        { "kind": "block", "type": "SOF" },
        { "kind": "block", "type": "StartUp" },
        { "kind": "block", "type": "Timer" },
        { "kind": "block", "type": "TXT" },
        { "kind": "block", "type": "WSCCB" },
        { "kind": "block", "type": "set_var" },
        { "kind": "block", "type": "compare_ex" },
        { "kind": "block", "type": "text"},
        { "kind": "block", "type": "Check_range"}
      ]
    },
    {
      "kind": "category",
      "name": "變數",
      "custom": "VARIABLE"
    },
    {
      "kind": "category",
      "name": "函式",
      "custom": "PROCEDURE"
    }
  ]
};

// =============================================================
// 4. 初始化函式 (start) - 修改為離線配置
// =============================================================
function start() {
  console.log("Blockly injecting...");

  // 建立 Workspace
  workspace = Blockly.inject('blocklyDiv', {
    toolbox: toolbox,
    
    // 指向本地 blockly/media 資料夾 (路徑相對於 index.html)
    media: 'blockly/media/',
    
    scrollbars: true,
    zoom: {
      controls: true,
      wheel: true,
      startScale: 1.0,
      maxScale: 3,
      minScale: 0.3,
      scaleSpeed: 1.2
    },
    trashcan: true
  });

  // 強制重繪 (防止初始化時高度為 0)
  setTimeout(function() {
      window.dispatchEvent(new Event('resize'));
      console.log("Blockly forced resize executed.");
  }, 200);
}

// =============================================================
// 5. 事件監聽 (輸出程式碼)
// =============================================================
document.addEventListener('DOMContentLoaded', () => {
  const saveButton = document.getElementById('saveButton');
  const codePre = document.getElementById('generatedCode');
  
  if (saveButton) {
    saveButton.addEventListener('click', () => {
      // 確保 workspace 已經初始化
      if (!workspace) {
          console.warn("Workspace not initialized");
          return;
      }

      // 檢查 Python 生成器
      // 使用的是 *_compressed.js，通常它會掛載在 Blockly.Python 底下
      let generator = null;
      if (typeof python !== 'undefined' && python.pythonGenerator) {
          generator = python.pythonGenerator;
      } else if (typeof Blockly !== 'undefined' && Blockly.Python) {
          generator = Blockly.Python;
      }

      if (generator) {
          try {
              const code = generator.workspaceToCode(workspace);
              console.log(code); 
              
              // 顯示在畫面上
              if (codePre) {
                  // 如果 pre 裡面有 code 標籤，就塞進 code 標籤，否則塞進 pre
                  const codeElement = codePre.querySelector('code') || codePre;
                  codeElement.innerText = code;
              }
          } catch (e) {
              console.error("生成程式碼錯誤: ", e);
              if (codePre) codePre.innerText = "生成錯誤: " + e.message;
          }
      } else {
          console.error("找不到 Python Generator，請檢查 python_custom.js 是否正確載入");
          if (codePre) codePre.innerText = "Error: Python Generator not found. 請檢查 python_compressed.js 是否載入";
      }
    });
  }
});
