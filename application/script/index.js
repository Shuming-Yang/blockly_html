'use strict';

let workspace = null;
let myProceduresList = [];
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

// 定義擴充邏輯
Blockly.Extensions.register('file_picker_extension', function() {
  // 監聽積木上的欄位點擊事件 (針對路徑欄位)
  const field = this.getField('path');

  // 綁定點擊邏輯
  field.showEditor_ = async function() {
    // 優先使用後端選檔案
    if (window.pywebview && window.pywebview.api) {
      const fileTypes = ['Text Files (*.txt)', 'All files (*.*)'];
      // 呼叫後端原子 API 獲取絕對路徑
      const result = await window.pywebview.api.select_file_dialog(window.projectDir || "", fileTypes);

      if (result && result.path) {
        const absPath = result.path;
        
        // 如果目前沒有專案目錄，則自動將選取檔案的所在資料夾設定為全域專案目錄
        if (!window.projectDir && typeof setCurrentFileStatus === 'function') {
          const { dir } = splitAbsolutePath(absPath);
          console.info("Auto-initializing project directory to:", dir);
          
          // 關鍵修正：維持當前檔名，僅更新目錄與修改狀態
          // 確保 dir 是正規化後的純目錄，並處理當前檔名為空的情況
          const currentFilename = window.filenameCurrent || "Undefined";
          const constructedPath = getAbsolutePath(dir, currentFilename);
          
          setCurrentFileStatus(constructedPath, true);
        }

        let projectDir = window.projectDir || "";
        let finalPath = absPath; // 預設使用絕對路徑

        // --- 前端業務邏輯：處理路徑相對化 ---
        if (projectDir) {
          /* 統一路徑格式並執行相對路徑化 */
          
          // 1. 統一路徑格式 (利用全域 normalizePath Helper，處理 Windows 大小寫不敏感)
          const normalizedAbs = normalizePath(absPath).toLowerCase();
          const normalizedProj = normalizePath(projectDir).toLowerCase();

          // 2. 安全校驗：選取路徑必須位於專案目錄下
          if (!normalizedAbs.startsWith(normalizedProj)) {
            alert('Please select a file within the current project directory to ensure project portability.');
            return;
          }

          // 3. 計算相對路徑：直接利用正規化後的結果進行擷取
          let relPath = normalizePath(absPath).substring(normalizedProj.length);
          if (relPath.startsWith('/')) {
            relPath = relPath.substring(1);
          }
          finalPath = relPath;
        }

        // 更新積木欄位數值
        field.setValue(finalPath);
      }
      return;
    }
  };
});

function getProcedureOptions() {
  // 如果清單為空，Blockly 要求至少要有一個選項，否則會報錯
  if (myProceduresList.length === 0) {
    return [["==To Create a new Timer==", "NONE"]];
  }

  // 將 ["Timer1", "Timer2"] 轉換為 [["Timer1", "Timer1"], ["Timer2", "Timer2"]]
  return myProceduresList.map(name => [name, name]);
}
// =============================================================
// 2. 積木定義 (JSON)
// =============================================================
const customBlocksJson = [
  {
    "type": "startup",
    "message0": "Startup %1",
    "args0": [
      { "type": "input_statement", "name": "statements" }
    ],
    "colour": 65,
    "tooltip": "Execute statements at the start of the program",
  },
  {
    "type": "int_task",
    "message0": "INT handler %1 %2",
    "args0": [
      {
        "type": "field_dropdown", "name": "NAME", "options": [
          ["SOF", "sof"], ["EOF", "eof"], ["Line", "line"], ["Timer", "timer"], ["FSIN", "fsin"]]
      },  
      { "type": "input_statement", "name": "STACK" }
    ],
    "colour": 65,
    "tooltip": "Execute statements at the start of the program",
  },
  {
    "type": "wait_until_timeout",
    "message0": "Wait for %1 event %2 do %3 or timeout after %4 ms %5 do %6",
    "args0": [
      {
        "type": "field_dropdown", "name": "event_sel", "options": [
          ["SOF", "sof"], ["EOF", "eof"], ["FSIN", "fsin"]]
      },
      { "type": "input_dummy" },
      { "type": "input_statement", "name": "do_func" },
      { "type": "field_input", "name": "timeout", "text": "100" },
      { "type": "input_dummy" },
      { "type": "input_statement", "name": "timeout_func" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 0,
    "tooltip": "Wait until the selected event occurs or timeout expires",
  },
  {
    "type": "read_device",
    "message0": "device id %1 address %2 length %3",
    "args0": [
      { "type": "field_hex", "name": "dev_id", "text": "6C" },
      { "type": "field_hex", "name": "address", "text": "300A" },
      {
        "type": "field_dropdown", "name": "length_sel", "options": [
          ['1byte', '1'], ['2bytes', '2'], ['3bytes', '3'], ['4bytes', '4']]
      }
    ],
    "output": "String",
    "colour": 40,
    "tooltip": "Read data from a device at given ID and address",
  },
  {
    "type": "placeholder_emb",
    "message0": "EMB (Auto-Detect)",
    "colour": 40,
    "tooltip": "This block will be automatically replaced based on the selected board.",
  },
  {
    "type": "emb",
    "message0": "%1 EMB offset %2 length %3",
    "args0": [
      {
        "type": "field_dropdown", "name": "emb_sel", "options": [
          ['Top', 'top'], ['Bottom', 'btm']]
      },
      { "type": "field_input", "name": "offset", "text": "00" },
      {
        "type": "field_dropdown", "name": "length_sel", "options": [
          ['1byte', '1'], ['2bytes', '2'], ['3bytes', '3'], ['4bytes', '4']]
      }
    ],
    "output": "String",
    "colour": 40,
    "tooltip": "Read EMB data from Top or Bottom with specified offset and length",
  },
  {
    "type": "emb_mcu",
    "message0": "%1 EMB offset %2",
    "args0": [
      {
        "type": "field_dropdown", "name": "vc_sel", "options": [
          ['VC0', 'vc0'], ['VC1', 'vc1'], ['VC2', 'vc2'], ['VC3', 'vc3']]
      },
      { "type": "field_input", "name": "offset", "text": "00" }
    ],
    "output": "String",
    "colour": 40,
    "tooltip": "Read EMB data from selected Virtual Channel (VC) at specified offset",
  },
  {
    "type": "get_var",
    "message0": "%1",
    "args0": [
      { "type": "field_variable", "name": "var", "variable": "Var0", "variableTypes": ["String"], "defaultType": "String" }
    ],
    "output": "String",
    "colour": 290,
    "tooltip": "Use a variable value",
  },
  {
    "type": "get_platform",
    "message0": "platform %1",
    "args0": [
      {
        "type": "field_dropdown", "name": "platform_value_sel", "options": [
          // ['Luminance', 'luminance'],
          ['Tick_1ms', 'tick_1ms'],
          // ['Err_status', 'Err_status'],
          // ['FPS', 'FPS'],
          // ['FPS_Min', 'FPS_Min'],
          // ['FPS_Max', 'FPS_Max']
        ]
      }
    ],
    "output": "String",
    "colour": 40,
    "tooltip": "Get a selected platform value",
  },
  {
    "type": "num_hex",
    "message0": "hex %1",
    "args0": [
      { "type": "field_hex", "name": "hex_text", "text": "FFFFFFFF" }
    ],
    "output": "String",
    "colour": 230,
    "tooltip": "Enter a hexadecimal value",
  },
  {
    "type": "num_dec",
    "message0": "%1",
    "args0": [
      { "type": "field_number", "name": "num_text", "text": "10" }
    ],
    "output": "String",
    "colour": 230,
    "tooltip": "Enter a decimal value",
  },
  {
    "type": "var_bitwise",
    "message0": "%1 %2 %3",
    "args0": [
      { "type": "input_value", "name": "a", "check": "String" },
      {
        "type": "field_dropdown", "name": "var_bitwise_operator", "options": [
          ['|', 'or'], ['&', 'and'], ['^', 'xor'], ['<<', 'lshift'], ['>>', 'rshift']
        ]
      },
      { "type": "input_value", "name": "b", "check": "String" },
    ],
    "inputsInline": true,
    "output": "String",
    "colour": 230,
    "tooltip": "Perform bitwise operation between two values",
  },
  {
    "type": "var_operation",
    "message0": "%1 %2 %3",
    "args0": [
      { "type": "input_value", "name": "a", "check": "String" },
      {
        "type": "field_dropdown", "name": "var_operator", "options": [
          ['+', 'add'], ['-', 'sub'], ['*', 'mul'], ['/', 'div'], ['%', 'mod']
        ]
      },
      { "type": "input_value", "name": "b", "check": "String" },
    ],
    "inputsInline": true,
    "output": "String",
    "colour": 230,
    "tooltip": "Perform arithmetic operation between two values",
  },
  {
    "type": "placeholder_gpio",
    "message0": "GPIO (Auto-Detect)",
    "colour": 250,
    "tooltip": "This block will be automatically replaced based on the selected board.",
  },
  {
    "type": "atb_gpio",
    "message0": "Set ATB %1 to %2",
    "args0": [
      {
        "type": "field_dropdown", "name": "gpio_sel", "options": [
          ['GPIO0', 'gpio0'], ['GPIO1', 'gpio1']]
      },
      {
        "type": "field_dropdown", "name": "state_sel", "options": [
          ['Low', 'low'], ['High', 'high'], ['Pulse', 'pulse']]
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 250,
    "tooltip": "Set ATB GPIO to Low, High, or Pulse",
  },
  {
    "type": "mcu_gpio",
    "message0": "Set MCU %1 to %2",
    "args0": [
      {
        "type": "field_dropdown", "name": "gpio_sel", "options": [
          ['GPIO0', 'gpio0'],
          ['GPIO1', 'gpio1'],
          ['GPIO2', 'gpio2'],
          ['GPIO3', 'gpio3']
        ]
      },
      {
        "type": "field_dropdown", "name": "state_sel", "options": [
          ['Low', 'low'], ['High', 'high'], ['Pulse', 'pulse']]
      }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 250,
    "tooltip": "Set MCU GPIO to Low, High, or Pulse",
  },
  {
    "type": "write_device",
    "message0": "Set device id %1 address %2 length %3 = %4",
    "args0": [
      { "type": "field_hex", "name": "dev_id", "text": "6c" },
      { "type": "field_hex", "name": "address", "text": "0100" },
      {
        "type": "field_dropdown", "name": "length_sel", "options": [
          ['1byte', '1'], ['2bytes', '2'], ['3bytes', '3'], ['4bytes', '4']]
      },
      { "type": "input_value", "name": "data", "check": "String" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 250,
    "tooltip": "Write data to device at given ID and address",
  },
  {
    "type": "abort",
    "message0": "Abort test",
    "previousStatement": null,
    "colour": 250,
    "tooltip": "Abort the current test",
  },
  {
    "type": "placeholder_config_adv",
    "message0": "Config adv",
    "colour": 40,
    "tooltip": "This block is advance.",
  },
  {
    "type": "config_mipi",
    "message0": "Config MIPI stream %1",
    "args0": [
     {
        "type": "field_dropdown", "name": "Stream", "options": [
           ['0', '0'], ['1', '1'], ['2', '2'], ['3', '3']]
      },
    ],
    "message1": "HSize %1 VSize%2",
    "args1": [
      { "type": "field_number", "name": "hsize", "text": "0000" },
      { "type": "field_number", "name": "vsize", "text": "0000" }
    ],
    "message2": "FTIME_MAX %1us FTIME_MIN %2us",
    "args2": [
      { "type": "field_number", "name": "ftime_max", "text": "0000" },
      { "type": "field_number", "name": "ftime_min", "text": "0000" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 250,
    "tooltip": "Starts the MIPI error monitor.\nA threshold > 0 begins tracing and also serves as the freeze threshold for SOF/EOF errors.\nUse checkboxes to enable specific error checks (SOF/EOF, packet size, CRC).",
  },
  {
    "type": "config_mipi_dt",
    "message0": "Config MIPI stream %1 VC %2 DT %3",
    "args0": [
     {
        "type": "field_dropdown", "name": "Stream", "options": [
           ['0', '0'], ['1', '1'], ['2', '2'], ['3', '3']]
      },
      {
        "type": "field_dropdown", "name": "VC", "options": [
           ['0', '0'], ['1', '1'], ['2', '2'], ['3', '3']]
      },
      { "type": "field_hex", "name": "DT", "text": "2d" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 250,
    "tooltip": "Starts the MIPI error monitor.\nA threshold > 0 begins tracing and also serves as the freeze threshold for SOF/EOF errors.\nUse checkboxes to enable specific error checks (SOF/EOF, packet size, CRC).",
  },
  {
    "type": "mipi_monitor",
    "message0": "Start MIPI monitor",
    "message1": "height_err%1 width_err%2",
    "args1": [
      { "type": "field_checkbox", "name": "height_err", "checked": false },
      { "type": "field_checkbox", "name": "width_err", "checked": false }
    ],
    "message2": "eof_mismatch_err%1 sof_mismatch_err%2",
    "args2": [
      { "type": "field_checkbox", "name": "eof_mismatch_err", "checked": false },
      { "type": "field_checkbox", "name": "sof_mismatch_err", "checked": false }
    ],
    "message3": "line_err%1 ecc_err%2 crc_err%3",
    "args3": [
      { "type": "field_checkbox", "name": "line_err", "checked": false },
      { "type": "field_checkbox", "name": "ecc_err", "checked": false },
      { "type": "field_checkbox", "name": "crc_err", "checked": false },
    ],
    "message4": "frame_rate_err0%1 frame_rate_err1%2",
    "args4": [
      { "type": "field_checkbox", "name": "frame_rate_err0", "checked": false },
      { "type": "field_checkbox", "name": "frame_rate_err1", "checked": false }
    ],
    "message5": "timeout_err%1 vc_dt_err%2",
    "args5": [
      { "type": "field_checkbox", "name": "timeout_err", "checked": false },
      { "type": "field_checkbox", "name": "vc_dt_err", "checked": false }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 250,
    "tooltip": "Starts the MIPI error monitor.\nA threshold > 0 begins tracing and also serves as the freeze threshold for SOF/EOF errors.\nUse checkboxes to enable specific error checks (SOF/EOF, packet size, CRC).",
  },
  {
    "type": "print_mipi",
    "message0": "print all mipi status",
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Prints all recorded values if an error is detected in the run txt command."
  },
  {
    "type": "set_var",
    "message0": "set %1 = %2",
    "args0": [
      { "type": "field_variable", "name": "var", "variable": "Var0", "variableTypes": ["String"], "defaultType": "String" },
      { "type": "input_value", "name": "data", "check": "String" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 290,
    "tooltip": "set variable",
  },
  {
    "type": "run_txt",
    "message0": "Run txt file %1",
    "args0": [
      { "type": "field_input", "name": "path", "text": "Open Browser..." }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 250,
    "tooltip": "Run the specified TXT file",
    "extensions": ["file_picker_extension"],
  },
  {
    "type": "compare_ex",
    "message0": "%1 %2 %3",
    "args0": [
      { "type": "input_value", "name": "a", "check": "String" },
      {
        "type": "field_dropdown", "name": "operator", "options": [
          ['==', 'eq'], ['\u2260', 'neq'], ['<', 'lt'],
          ['\u2264', 'lte'], ['>', 'gt'], ['\u2265', 'gte']]
      },
      { "type": "input_value", "name": "b", "check": "String" }
    ],
    "inputsInline": true,
    "output": "Boolean",
    "colour": 210,
    "tooltip": "Compare two values using the selected operator",
  },
  {
    "type": "controls_if_custom",
    "message0": "if %1 %2 %3 %4",
    "args0": [
      { "type": "input_value", "name": "a", "check": "String" },
      {
        "type": "field_dropdown", "name": "operator", "options": [
          ['==', 'eq'], ['\u2260', 'neq'], ['<', 'lt'],
          ['\u2264', 'lte'], ['>', 'gt'], ['\u2265', 'gte']]
      },
      { "type": "input_value", "name": "b", "check": "String" },
      { "type": "input_dummy" }
    ],
    "message1": "do %1",
    "args1": [
      { "type": "input_statement", "name": "do" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "style": "logic_blocks",
    "helpUrl": "%{B_CONTROLS_IF_HELPURL}",
    "mutator": "controls_if_mutator" // 保留官方的 mutator 功能（else/else if）
  },
  {
    "type": "controls_repeat_ext_ex",
    "message0": "repeat %1 times",
    "args0": [
      { "type": "field_input", "name": "times", "text": "5" }
    ],
    "message1": "do %1",
    "args1": [
      { "type": "input_statement", "name": "do" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "style": "loop_blocks",
    "tooltip": "Repeat the enclosed statements a number of times",
  },
  {
    "type": "controls_whileUntil_ex",
    "message0": "repeat %1 if %2 %3 %4 %5",
    "args0": [
      {
        "type": "field_dropdown", "name": "mode", "options": [
          ['while', 'while'], ['until', 'until']]
      },
      { "type": "input_value", "name": "a", "check": "String" },
      {
        "type": "field_dropdown", "name": "operator", "options": [
          ['==', 'eq'], ['\u2260', 'neq'], ['<', 'lt'],
          ['\u2264', 'lte'], ['>', 'gt'], ['\u2265', 'gte']]
      },
      { "type": "input_value", "name": "b", "check": "String" },
      { "type": "input_dummy" }
    ],
    "message1": "do %1",
    "args1": [
      { "type": "input_statement", "name": "do" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "style": "loop_blocks",
    "tooltip": "Repeat the enclosed statements a number of times",
  },
  {
    "type": "delay",
    "message0": "Delay %1 %2",
    "args0": [
      { "type": "field_number", "name": "time", "text": "0000" },
      {
        "type": "field_dropdown", "name": "time_unit", "options": [
          ["ms", "ms"], ["us", "us"]]
      },
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 0,
    "tooltip": "Delay",
  },
  {
    "type": "random_int",
    "message0": "random integer from %1 to %2",
    "args0": [
      { "type": "field_number", "name": "min", "text": "0000" },
      { "type": "field_number", "name": "max", "text": "0100" },
    ],
    "inputsInline": true,
    "output": "String",
    "colour": 230,
    "tooltip": "Generate a random integer between min and max",
  },
  {
    "type": "print",
    "message0": "Print %1",
    "args0": [
      { "type": "input_value", "name": "print", "check": "print_string" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 160,
    "tooltip": "Print a value or text",
  },
  {
    "type": "text",
    "message0": "\"%1\" %2",
    "args0": [
      { "type": "field_input", "name": "text", "text": "" },
      { "type": "input_value", "name": "next_text", "check": "print_string" }
    ],
    "output": "print_string",
    "colour": 160,
    "tooltip": "Text for printing",
  },
  {
    "type": "variable_text",
    "message0": "\"%1\" %2",
    "args0": [
      { "type": "field_variable", "name": "var", "variable": "var0", "variableTypes": ["String"], "defaultType": "String" },
      { "type": "input_value", "name": "next_text", "check": "print_string" }
    ],
    "output": "print_string",
    "colour": 160,
    "tooltip": "Variable for printing",
  },
  {
    "type": "all_records_text",
    "message0": "all records text",
    "output": "print_string",
    "colour": 160,
    "tooltip": "Prints all recorded values if an error is detected in the run txt command."
  },
  {
    "type": "newline_text",
    "message0": "\"\\n\"",
    "output": "print_string",
    "colour": 160,
    "tooltip": "Print a newline character",
  },
  {
    "type": "create_timer",
    "message0": "Create Timer Thread after %1 ms",
    "args0": [
      { "type": "field_number", "name": "time", "text": "0000" }
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 380,
    "tooltip": "Declare a repeating timer every specified milliseconds",
  },
  {
    "type": "create_timer_random",
    "message0": "Create timer Random after %1 ~ %2 ms",
    "args0": [
      { "type": "field_number", "name": "min", "text": "0000" },
      { "type": "field_number", "name": "max", "text": "0100" },
    ],
    "previousStatement": null,
    "nextStatement": null,
    "colour": 380,
    "tooltip": "Declare a repeating timer every random milliseconds",
  },
  {
    "type": "return_void",
    "message0": "Return",
    "previousStatement": null,
    "colour": 290,
    "tooltip": "Return from function (no value)",
  },
  {
    "type": "loop_control",
    "message0": "%1 of loop",
    "args0": [
      { "type": "field_dropdown", "name": "action_sel", "options": [
          [ "break", "break" ],[ "continue", "continue" ]]  }
    ],
    "previousStatement": null,   
    "colour": 120,
    "tooltip": "Break or continue the current loop",
    "helpUrl": ""
  }
];

// 註冊積木定義
Blockly.defineBlocksWithJsonArray(customBlocksJson);

// =============================================================
// [Added] Validation Logic for loading
// =============================================================
const BLOCK_DEFINITIONS = {};
customBlocksJson.forEach(def => {
  BLOCK_DEFINITIONS[def.type] = def;
});

function validateSerialization(state) {
  const warnings = [];
  if (!state || !state.blocks || !state.blocks.blocks) return warnings;

  // 建立一個暫時的 Headless Workspace，用於實例化積木以驗證動態輸入
  const validationWs = new Blockly.Workspace();

  function traverse(block) {
    // 1. Check Block Type
    if (!Blockly.Blocks[block.type]) {
      warnings.push(`- Unknown Block: ${block.type}`);
    } else {
      // 2. Check Fields and Inputs against Definition
      const def = BLOCK_DEFINITIONS[block.type];
      if (def) {
        const definedFields = new Set();
        const definedInputs = new Set();

        // Dynamically find the maximum index N used in argsN
        let maxIndex = -1;
        Object.keys(def).forEach(key => {
          const match = key.match(/^args(\d+)$/);
          if (match) {
            const index = parseInt(match[1], 10);
            if (index > maxIndex) maxIndex = index;
          }
        });

        // Iterate through all indices up to maxIndex
        for (let i = 0; i <= maxIndex; i++) {
          const args = def['args' + i];
          if (!args) continue; // Skip if this specific row has no arguments (fields/inputs)

          args.forEach(arg => {
            if (arg.type.startsWith('field_')) {
              if (arg.name) definedFields.add(arg.name);
            } else if (arg.type.startsWith('input_')) {
              if (arg.name) definedInputs.add(arg.name);
            }
          });
        }

        const savedFields = block.fields || {};
        const savedInputs = block.inputs || {};

        // Check for Extra/Missing Fields
        Object.keys(savedFields).forEach(key => {
          if (!definedFields.has(key)) {
            warnings.push(`- Extra Field in ${block.type}: ${key}`);
          }
        });
        definedFields.forEach(key => {
          if (savedFields[key] === undefined) {
            warnings.push(`- Missing Field in ${block.type}: ${key}`);
          }
        });

        // Check for Extra Inputs
        Object.keys(savedInputs).forEach(key => {
          if (!definedInputs.has(key)) {
            let isValidDynamic = false;

            // 如果積木有 mutator，我們嘗試在背景實例化該積木，讓積木自己告訴我們這個輸入是否合法
            if (def.mutator) {
              try {
                // 1. 建立積木狀態的淺層副本 (只保留屬性與 extraState/mutation)
                const tempState = Object.assign({}, block);
                // 2. 移除子積木與連接資訊，避免遞迴載入，只驗證當前積木結構
                delete tempState.inputs;
                delete tempState.next;
                delete tempState.block;
                delete tempState.id; // 避免 ID 衝突

                // 3. 在暫存區實例化積木
                const tempBlock = Blockly.serialization.blocks.append(tempState, validationWs);

                // 4. 檢查實例化後的積木是否有這個輸入
                if (tempBlock.getInput(key)) {
                  isValidDynamic = true;
                }

                tempBlock.dispose();
              } catch (e) {
                // 若實例化失敗 (例如缺少 extension)，則保守起見視為合法，避免誤報
                isValidDynamic = true;
              }
            }

            if (!isValidDynamic) {
              warnings.push(`- Extra Input in ${block.type}: ${key}`);
            }
          }
        });

        // Check Dropdown Options
        for (let i = 0; i <= maxIndex; i++) {
          const args = def['args' + i];
          if (!args) continue;
          args.forEach(arg => {
            if (arg.type === 'field_dropdown' && Array.isArray(arg.options) && arg.name) {
              const savedValue = savedFields[arg.name];
              if (savedValue !== undefined) {
                // arg.options is [[label, value], ...]
                const isValid = arg.options.some(opt => opt[1] === savedValue);
                if (!isValid) {
                  warnings.push(`- Invalid Option in ${block.type} (${arg.name}): ${savedValue}`);
                }
              }
            }
          });
        }
      }
    }

    // Recurse
    if (block.next && block.next.block) traverse(block.next.block);
    if (block.inputs) {
      Object.values(block.inputs).forEach(input => {
        if (input.block) traverse(input.block);
        if (input.shadow) traverse(input.shadow);
      });
    }
  }

  state.blocks.blocks.forEach(traverse);
  validationWs.dispose(); // 驗證結束後清理暫存區
  return warnings;
}

// Monkey patch load to intercept and validate
const originalLoad = Blockly.serialization.workspaces.load;
Blockly.serialization.workspaces.load = function(state, workspace, options) {
  try {
    const warnings = validateSerialization(state);
    if (warnings.length > 0) {
      const msg = "Warning: Incompatible blocks or options detected:\n" + warnings.join("\n");
      console.warn(msg);
      alert(msg);
    }
  } catch (e) {
    console.error("Validation failed:", e);
  }
  return originalLoad.call(this, state, workspace, options);
};

// =============================================================
// 3. Toolbox 定義 (JSON Format)
// =============================================================
// 基本 Toolbox，不包含特定板子的部分
const baseToolbox = {
  "kind": "categoryToolbox",
  "contents": [
    {
      "kind": "category",
      "name": "Logic",
      "contents": [
        { "kind": "block", "type": "controls_if_custom"},
        { "kind": "block", "type": "compare_ex"}
      ]
    },
    {
      "kind": "category",
      "name": "Loops",
      "contents": [
        { "kind": "block", "type": "controls_repeat_ext_ex"},
        { "kind": "block", "type": "controls_whileUntil_ex"},
        { "kind": "block", "type": "loop_control" }
      ]
    },
    {
      "kind": "category",
      "name": "Math",
      "contents": [
        { "kind": "block", "type": "num_hex"},
        { "kind": "block", "type": "num_dec"},
        { "kind": "block", "type": "random_int"},
        { "kind": "block", "type": "var_bitwise"},
        { "kind": "block", "type": "var_operation"}
      ]
    },
    {
      "kind": "category",
      "name": "Device",
      "custom": "DYNAMIC_DEVICE",
      "contents": [
        { "kind": "block", "type": "read_device" },
        { "kind": "block", "type": "placeholder_emb" },
        { "kind": "block", "type": "get_platform" },
        { "kind": "block", "type": "run_txt" },
        { "kind": "block", "type": "write_device" },
        { "kind": "block", "type": "placeholder_gpio" },
        { "kind": "block", "type": "abort" }
      ]
    },
    {
      "kind": "category",
      "name": "Timing",
      "contents": [
        { "kind": "block", "type": "wait_until_timeout" },
        { "kind": "block", "type": "delay"}
      ]
    },
    {
      "kind": "category",
      "name": "Output",
      "contents": [
        { "kind": "block", "type": "print" },
        { "kind": "block", "type": "text" },
        { "kind": "block", "type": "variable_text" },
        { "kind": "block", "type": "all_records_text" },
        { "kind": "block", "type": "newline_text" }
      ]
    },
    {
      "kind": "category",
      "name": "Variables",
      "custom": "VARIABLE"
    },
    {
      "kind": "category",
      "name": "Function / Group",
      "custom": "MY_PROCEDURE"
    },
    {
      "kind": "category",
      "name": "Advance",
      "custom": "DYNAMIC_ADVANCE",
      "contents": [
        { "kind": "block", "type": "placeholder_config_adv" }
      ]
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
    toolbox: baseToolbox,
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
    trashcan: true,
    maxInstances: {
      'startup': 1,
    },
  });

  // 強制重繪 (防止初始化時高度為 0)
  setTimeout(function() {
    window.dispatchEvent(new Event('resize'));
    console.log("Blockly forced resize executed.");
  }, 200);
  Create_customer_variable();
  create_cutomer_procedures();
  create_customer_toolbox();
  initial_blocks();
  update_toolbox(window.GLOBAL_BOARD_ID);
}

//===========Create_customer_variable==============
function Create_customer_variable() {
  workspace.registerButtonCallback('CREATE_VARIABLE', function(button) {
    Blockly.Variables.createVariableButtonHandler(button.getTargetWorkspace(), (varName) => {
      console.log("Variable create done: " + varName);
    }, 'String'); // 這裡可以限制變數類型
  });

  workspace.registerToolboxCategoryCallback('VARIABLE', function(Tworkspace) {
    const xmlList = [];
    // --- 初始自動建立變數邏輯 ---
    // 檢查目前是否已經有任何變數，如果沒有，則主動建立一個
    const allVars = workspace.getAllVariables();
    if (allVars.length === 0) {
      // 建立一個名為 'my_variable'，型別為 'String' 的初始變數
      workspace.createVariable('var0', 'String');
    }
    // 1. (選配) 加入「建立變數」按鈕
    const button = document.createElement('button');
    button.setAttribute('text', '＋ Create Variable');
    button.setAttribute('callbackKey', 'CREATE_VARIABLE');
    xmlList.push(button);

    // 加入你的積木
    xmlList.push(Blockly.utils.xml.textToDom('<block type="get_var"></block>'));
    xmlList.push(Blockly.utils.xml.textToDom('<block type="set_var"></block>'));

    return xmlList;
  });
}

function create_cutomer_procedures() {
  workspace.registerToolboxCategoryCallback('MY_PROCEDURE', function(workspace) {
    // 1. 取得官方自動生成的函式清單 (含 defnoreturn, callnoreturn 等)
    let xmlList = Blockly.Procedures.flyoutCategory(workspace);

    // 2. 過濾掉不需要的 (例如移除有回傳值的積木)
    xmlList = xmlList.filter(node =>
      node.getAttribute('type') !== 'procedures_defreturn' &&
      node.getAttribute('type') !== 'procedures_callreturn' &&
      node.getAttribute('type') !== 'procedures_ifreturn'
    );

    xmlList.push(Blockly.utils.xml.textToDom('<block type="return_void"></block>'));

    return xmlList;
  });

  const oldInit = Blockly.Blocks['procedures_defnoreturn'].init;

  // 覆寫並移除 mutator
  Blockly.Blocks['procedures_defnoreturn'].init = function() {
    oldInit.call(this);
    this.setMutator(null); // 明確將 Mutator 設為 null
  };

}

function create_customer_toolbox() {
  workspace.registerToolboxCategoryCallback('DYNAMIC_ADVANCE', function(workspace) {
    // Use 'custom' property instead of 'name' for stability
    const categoryDef = baseToolbox.contents.find(c => c.custom === 'DYNAMIC_ADVANCE');
    let contents = categoryDef ? JSON.parse(JSON.stringify(categoryDef.contents)) : [];
    const boardId = String(window.GLOBAL_BOARD_ID || '1'); // Default to MCU

    // 處理僅限 MCU 的積木
    if (boardId === '1') {
      const index = contents.findIndex(c => c.type === 'placeholder_config_adv');
      if (index !== -1) {
        contents.splice(index, 1, 
        { "kind": "block", "type": "config_mipi" },
        { "kind": "block", "type": "config_mipi_dt" },
        { "kind": "block", "type": "mipi_monitor" },
        { "kind": "block", "type": "print_mipi" }
        );
      }
    } else {
      const index = contents.findIndex(c => c.type === 'placeholder_config_adv');
      if (index !== -1) {
        contents.splice(index, 1,
        { "kind": "block", "type": "int_task" },
        { "kind": "block", "type": "create_timer" },
        { "kind": "block", "type": "create_timer_random" }
        );
      }
    }
    return contents;
  });
  workspace.registerToolboxCategoryCallback('DYNAMIC_DEVICE', function(workspace) {
    // Use 'custom' property instead of 'name' for stability
    const categoryDef = baseToolbox.contents.find(c => c.custom === 'DYNAMIC_DEVICE');
    let contents = categoryDef ? JSON.parse(JSON.stringify(categoryDef.contents)) : [];
    const boardId = String(window.GLOBAL_BOARD_ID || '1'); // Default to MCU

    // 處理通用佔位符替換
    const embBlock = contents.find(c => c.type === 'placeholder_emb');
    if (embBlock) {
      embBlock.type = (boardId === '1') ? 'emb_mcu' : 'emb';
    }

    const gpioBlock = contents.find(c => c.type === 'placeholder_gpio');
    if (gpioBlock) {
      gpioBlock.type = (boardId === '1') ? 'mcu_gpio' : 'atb_gpio';
    }
    return contents;
  });
}

function initial_blocks() {
  // ============= 初始化面 ===================
  // 1. 定義初始的 startup 積木資料
  const initialBlocks = {
    'blocks': {
      'languageVersion': 0,
      'blocks': [
        {
          'type': 'startup',
          'x': 50,
          'y': 50,
          'deletable': false,
        }
      ]
    }
  };

  const originalClear = workspace.clear.bind(workspace);

  // 2. 定義你的「強制回補」邏輯
  const ensureStartupBlock = () => {
    if (workspace.getAllBlocks(false).length === 0) {
      Blockly.Events.disable();
      try {
        Blockly.serialization.workspaces.load(initialBlocks, workspace);
      } finally {
        Blockly.Events.enable();
      }
    }
  };

  // 3. 重寫 workspace.clear
  workspace.clear = function () {
    Blockly.Events.disable(); // 禁用事件 - 不要進到垃圾桶

    originalClear();       // 先執行原本的清空動作
    if(workspace.trashcan) {
      workspace.trashcan.emptyContents(); // 清空垃圾桶
    }
    myProceduresList = []; // 清空 Timer 清單
    ensureStartupBlock();  // 清完立刻補上 startup 積木

    Blockly.Events.enable(); // 完成後重新啟用事件
  };

  // 4. 網頁打開時立即執行一次
  ensureStartupBlock();
}

function update_dynamic_toolbox(cus_lis){
  // console.log(cus_lis.timer.myProceduresList);
  myProceduresList = cus_lis.timer.myProceduresList;
  workspace.getToolbox().refreshSelection();
}

function update_toolbox(board){
  let boardName = "Unknown Board";
  if (parseInt(board, 10) === 1) {
    boardName = "MCU Board";
  } else if (parseInt(board, 10) === 2) {
    boardName = "ATB Board";
  }
  console.log("Target is", boardName, "\n");
  const newToolbox = JSON.parse(JSON.stringify(baseToolbox));

  workspace.updateToolbox(newToolbox);
  return validateBlocksOnWorkspace(); // 新增：更新工具箱後，驗證工作區中的積木，並回傳結果
}

function return_dynamic_block(){
  let cust_list = { 'timer':{myProceduresList}};
  return cust_list;
}

/**
 * Traverses the live toolbox to get a set of all visible block types.
 * This function relies on the toolbox already being updated for the current board.
 * It correctly handles static categories, and dynamic categories by invoking their callbacks.
 * @returns {Set<string>} A set of all visible block types in the current toolbox.
 */
function getVisibleBlockTypesFromToolbox() {
  const toolbox = workspace.getToolbox();
  if (!toolbox) {
    console.warn("getVisibleBlockTypesFromToolbox: Toolbox not found.");
    return new Set();
  }

  const types = new Set();

  /**
   * Recursively traverses toolbox items (live objects or JSON definitions).
   * @param {Array<Blockly.IToolboxItem|Blockly.utils.toolbox.ToolboxItemInfo|Element>} items 
   */
  function traverse(items) {
    if (!items || typeof items.forEach !== 'function') return;

    items.forEach(item => {
      if (!item) return; // Skip null/undefined items in the array
      const itemName = item.name_ || item.id || item.kind || item.tagName || 'unknown_item';

      try {
      // Case 1: It's a live IToolboxItem object (e.g., a category).
      // The `getContents` method will trigger the callback for dynamic categories.
        if (typeof item.getContents === 'function') {
          const contents = item.getContents();
          // The result of getContents can be an array of JSON, an array of XML,
          // or for some dynamic categories, it might be null or not an array.
          if (Array.isArray(contents)) {
            traverse(contents);
          } else if (typeof contents === 'string') {
            // If contents is a string, it is the custom key for a dynamic category.
            const callback = workspace.getToolboxCategoryCallback(contents);
            if (typeof callback === 'function') {
              const dynamicContents = callback(workspace);
              // The callback returns the definition (array), so we traverse it.
              traverse(dynamicContents);
            }
          } else if (contents) {
            console.warn(`Toolbox item '${itemName}' returned non-array contents. Wrapping in array.`, contents);
            traverse([contents]);
          }
        }
        // Case 2: It's a JSON definition (often returned by a dynamic callback).
        else if (item.kind) {
          if (item.kind === 'category') {
            // Handle nested dynamic categories in JSON definitions
            if (item.custom) {
              const callback = workspace.getToolboxCategoryCallback(item.custom);
              if (typeof callback === 'function') {
                const dynamicContents = callback(workspace);
                traverse(dynamicContents);
              }
            } else {
              // Standard category with contents
              traverse(item.contents);
            }
          } else if (item.kind === 'block' && item.type) {
            if (!item.type.startsWith('placeholder_')) {
              types.add(item.type);
            }
          }
        }
        // Case 3: It's an XML Element (also returned by some dynamic callbacks).
        else if (item.tagName) {
          if (item.tagName.toLowerCase() === 'block' && item.getAttribute('type')) {
            types.add(item.getAttribute('type'));
          }
        }
      } catch (e) {
        console.error(`Error processing toolbox item '${itemName}':`, e);
      }
    });
  }

  traverse(toolbox.getToolboxItems());
  return types;
}
/**
 * 檢查工作區中的積木是否適用於當前選擇的板子。
 * 不適用的積木將被禁用並顯示警告。
 */
function validateBlocksOnWorkspace() {
  const allBlocks = workspace.getAllBlocks(false);

  // Get the list of all blocks currently visible in the toolbox.
  // This is now the single source of truth.
  const validBlockTypes = getVisibleBlockTypesFromToolbox();

  const COMPATIBILITY_REASON = 'board_incompatible'; // 定義一個唯一的禁用原因
  let isValid = true;

  allBlocks.forEach(block => {
    // 增加一個保護，避免對 'startup' 積木進行操作。
    if (block.type === 'startup' || block.isInsertionMarker()) {
      return;
    }

    const blockType = block.type;
    // 如果當前積木類型不在有效列表裡，則視為無效
    const isInvalid = !validBlockTypes.has(blockType);

    if (isInvalid) {
      isValid = false;
      const warningText = `The block (${blockType}) is not supported in the current toolbox.`;
      // 如果積木無效，使用 setDisabledReason 禁用它並設置警告
      block.setDisabledReason(true, COMPATIBILITY_REASON);
      block.setWarningText(warningText);
    } else {
      // 如果積木變得有效，則僅移除因板子不相容而設置的禁用狀態與警告
      if (block.hasDisabledReason(COMPATIBILITY_REASON)) {
          block.setDisabledReason(false, COMPATIBILITY_REASON);
          block.setWarningText(null);
      }
    }
  });
  return isValid;
}

// =============================================================
// 5. Flattening Utility (Added)
// =============================================================
/**
 * 將 Workspace 的積木邏輯扁平化為標準 Blockly State
 * 
 * 需求與功能描述：
 * 1. **巢狀運算扁平化 (Expression Flattening)**：
 *    將複雜的巢狀運算 (如 `a = b * c + d`) 拆解為線性的暫存變數賦值 (如 `tmp0 = b * c`, `tmp1 = tmp0 + d`, `a = tmp1`)。
 *    這類似於編譯器的三位址碼 (Three-Address Code) 生成。
 * 
 * 2. **暫存變數複用 (Temp Variable Reuse)**：
 *    透過 `TempManager` 機制，當暫存變數 (`tmpX`) 的值被讀取後，該變數即視為可回收，
 *    供後續運算重複使用，以最小化變數使用量。
 * 
 * 3. **控制流程函式化 (Extract Control Flow to Functions)**：
 *    將 `if`、`loop` 等控制結構內部的積木區塊 (Do/Else) 自動提取為獨立的函式 (`func_flatten_N`)，
 *    並在原位置替換為函式呼叫。這有助於簡化主流程的視覺複雜度。
 * 
 * 4. **迴圈條件自動更新 (Loop Condition Update)**：
 *    針對 `while` 迴圈，自動偵測條件式中使用的變數，並將其計算邏輯複製一份至迴圈底端，
 *    確保迴圈在每次迭代時都能取得最新的條件值。
 * 
 * 5. **型別與連接檢查 (Type Safety & Connection Check)**：
 *    在拆解過程中進行嚴格的型別檢查 (如 String/Boolean)，防止不合法的連接導致錯誤。
 *    同時處理 `set_var` 的特殊情況 (如常數賦值不拆解)。
 * 
 * 產出：可以直接匯入 Blockly 進行視覺化檢查的 JSON 物件
 */
function flattenWorkspace() {
  console.log("=== flattenWorkspace Start ===\n");
  
  // [Fix] 定義 inputTypes 以相容舊版 Blockly (避免 undefined error)
  const inputTypes = Blockly.inputTypes || {
    VALUE: 1,
    STATEMENT: 3,
    DUMMY: 5
  };

  // 1. 複製當前 Workspace 到一個臨時 Workspace (Headless)
  const state = Blockly.serialization.workspaces.save(workspace);
  const tempWs = new Blockly.Workspace();
  try {
    Blockly.serialization.workspaces.load(state, tempWs);
  } catch (e) {
    console.error("Failed to load state into temp workspace:", e);
    throw e;
  }

  // [New] TempManager class for variable reuse
  class TempManager {
    constructor(workspace) {
      this.workspace = workspace;
      this.counter = 0;
      this.pool = []; // pool of { name, id }
    }
  
    get() {
      if (this.pool.length > 0) {
        const variableInfo = this.pool.pop();
        console.debug(`     [Temp] Reusing temp var: ${variableInfo.name}`);
        return variableInfo;
      }
      const name = 'tmp' + (this.counter++);
      const variable = this.workspace.createVariable(name, 'String');
      const variableInfo = { name, id: variable.getId() };
      console.debug(`     [Temp] Created new temp var: ${variableInfo.name} (ID: ${variableInfo.id})`);
      return variableInfo;
    }
  
    release(variableInfo) {
      if (variableInfo && variableInfo.name && variableInfo.name.startsWith('tmp')) {
        if (!this.pool.some(v => v.id === variableInfo.id)) {
          console.debug(`     [Temp] Releasing temp var: ${variableInfo.name}`);
          this.pool.push(variableInfo);
        }
      }
    }
  }

  const tempManager = new TempManager(tempWs);

  // [Added] Function counter for extracted do-blocks
  let funcCounter = 0;
  function getFuncName() {
    return 'func_flatten_' + (funcCounter++);
  }

  // [Added] Extract body to function
  function extractToFunction(input, bodyBlock) {
    const funcName = getFuncName();
    console.debug(`     Extracting body to function: ${funcName}`);

    // 1. Create Definition
    const defBlock = tempWs.newBlock('procedures_defnoreturn');
    defBlock.setFieldValue(funcName, 'NAME');
    // Move to avoid visual clutter
    defBlock.moveBy(500, funcCounter * 200); 

    // 2. Move body
    input.connection.disconnect();
    defBlock.getInput('STACK').connection.connect(bodyBlock.previousConnection);

    // 3. Create Call
    const callBlock = tempWs.newBlock('procedures_callnoreturn');
    callBlock.setFieldValue(funcName, 'NAME');
    if (callBlock.loadExtraState) {
      callBlock.loadExtraState({ name: funcName });
    }

    // 4. Connect Call
    input.connection.connect(callBlock.previousConnection);
  }

  // 判斷是否為簡單數值 (不需要拆解)
  function isSimpleValue(block) {
    if (!block) return true;
    const type = block.type;
    // 1. 變數讀取 (get_var)
    if (type === 'get_var') return true;
    // 2. 字串相關 (text, variable_text, newline_text) - 不拆解
    if (type === 'text' || type === 'variable_text' || type === 'newline_text') return true;
    return false;
  }

  // 判斷是否為純常數 (num_dec, num_hex)
  function isConstant(block) {
    if (!block) return false;
    return block.type === 'num_dec' || block.type === 'num_hex';
  }

  // [Added] Check if the input belongs to a loop condition
  function isLoopCondition(block, input) {
    // [Fix] For while loops, treat ALL value inputs as part of the condition.
    // This ensures nested expressions (e.g. a + b) are also updated in the loop.
    if (block.type === 'controls_whileUntil_ex' || block.type === 'controls_whileUntil') {
      return true;
    }
    return false;
  }

  // [Added] Helper to recursively release temps used in value inputs
  function releaseTemps(block) {
    if (!block) return;
    block.inputList.forEach(input => {
      if (input.type === inputTypes.VALUE) {
        const targetBlock = input.connection.targetBlock();
        if (targetBlock) {
          if (targetBlock.type === 'get_var') {
            const variableId = targetBlock.getFieldValue('var');
            const variable = tempWs.getVariableById(variableId);
            if (variable) {
              tempManager.release({ name: variable.name, id: variable.getId() });
            }
          } else {
            // Recurse into complex value blocks (like compare, operation)
            // These blocks are part of the expression tree rooted at this statement
            releaseTemps(targetBlock);
          }
        }
      }
    });
  }

  // [Added] Function to transform if-elif-else into nested if-else
  function transformIfElif(ifBlock) {
    // 1. Robustly determine the number of elifs
    let elifCount = ifBlock.elseifCount_;
    if (typeof elifCount !== 'number') {
      elifCount = 0;
      while (ifBlock.getInput('IF' + (elifCount + 1))) {
        elifCount++;
      }
      ifBlock.elseifCount_ = elifCount;
    }

    if (elifCount < 1) {
      return;
    }
    console.debug(`  -> Transforming if-elif block: ${ifBlock.id} (found ${elifCount} elifs)`);

    // 2. Create the nested block (Custom controls_if_custom)
    const nestedIfBlock = ifBlock.workspace.newBlock('controls_if_custom');
    nestedIfBlock.elseifCount_ = elifCount - 1;
    nestedIfBlock.elseCount_ = ifBlock.elseCount_ || (ifBlock.getInput('ELSE') ? 1 : 0);
    
    // Initialize shape of nested block
    if (nestedIfBlock.updateShape_) {
      nestedIfBlock.updateShape_();
    }

    // 3. Move IF1/DO1 from Original to a/b/do of Nested
    const if1 = ifBlock.getInput('IF1');
    const do1 = ifBlock.getInput('DO1');
    
    if (if1 && if1.connection.targetBlock()) {
      const target = if1.connection.targetBlock();
      // Try to unwrap compare_ex to fit into controls_if_custom
      if (target.type === 'compare_ex') {
        const valA = target.getInput('a');
        const valB = target.getInput('b');
        const op = target.getFieldValue('operator');

        if1.connection.disconnect(); // Disconnect from parent

        if (valA && valA.connection.targetBlock()) {
          const blockA = valA.connection.targetBlock();
          valA.connection.disconnect();
          nestedIfBlock.getInput('a').connection.connect(blockA.outputConnection);
        }
        if (valB && valB.connection.targetBlock()) {
          const blockB = valB.connection.targetBlock();
          valB.connection.disconnect();
          nestedIfBlock.getInput('b').connection.connect(blockB.outputConnection);
        }
        nestedIfBlock.setFieldValue(op, 'operator');
        target.dispose(); // Remove the now-empty compare_ex block
      } else {
        console.warn(`[Transform] Cannot map ${target.type} to controls_if_custom (expected compare_ex).`);
        if1.connection.disconnect();
      }
    }
    if (do1 && do1.connection.targetBlock()) {
      const target = do1.connection.targetBlock();
      do1.connection.disconnect();
      nestedIfBlock.getInput('do').connection.connect(target.previousConnection);
    }

    // 4. Move remaining ELIFs (IF2->IF1, etc.)
    for (let i = 1; i < elifCount; i++) {
      const srcIf = ifBlock.getInput('IF' + (i + 1));
      const srcDo = ifBlock.getInput('DO' + (i + 1));
      const dstIf = nestedIfBlock.getInput('IF' + i);
      const dstDo = nestedIfBlock.getInput('DO' + i);
      
      if (srcIf && srcIf.connection.targetBlock()) {
        const target = srcIf.connection.targetBlock();
        srcIf.connection.disconnect();
        dstIf.connection.connect(target.outputConnection);
      }
      if (srcDo && srcDo.connection.targetBlock()) {
        const target = srcDo.connection.targetBlock();
        srcDo.connection.disconnect();
        dstDo.connection.connect(target.previousConnection);
      }
    }

    // 5. Move ELSE
    const srcElse = ifBlock.getInput('ELSE');
    if (srcElse && srcElse.connection.targetBlock()) {
      const target = srcElse.connection.targetBlock();
      srcElse.connection.disconnect();
      nestedIfBlock.getInput('ELSE').connection.connect(target.previousConnection);
    }

    // 6. Clean up Original Block
    // Manually remove inputs to ensure they are gone, regardless of updateShape_ behavior on custom blocks
    for (let i = 1; i <= elifCount; i++) {
      if (ifBlock.getInput('IF' + i)) ifBlock.removeInput('IF' + i);
      if (ifBlock.getInput('DO' + i)) ifBlock.removeInput('DO' + i);
    }
    
    // Ensure ELSE input exists on original block to hold the nested block
    if (!ifBlock.getInput('ELSE')) {
      ifBlock.appendStatementInput('ELSE');
    }

    // Update state properties
    ifBlock.elseifCount_ = 0;
    ifBlock.elseCount_ = 1;
    
    // Try to sync shape if possible (for serialization consistency)
    if (ifBlock.updateShape_) {
      try {
        ifBlock.updateShape_();
      } catch (e) {
        console.warn("  [Warn] updateShape_ failed on original block, relying on manual input removal.", e);
      }
    }

    // 7. Connect Nested Block to Original's ELSE
    ifBlock.getInput('ELSE').connection.connect(nestedIfBlock.previousConnection);
    
    // 8. Recurse on the nested block (it might still have multiple elifs if original had > 2)
    if (nestedIfBlock.elseifCount_ > 0) {
      transformIfElif(nestedIfBlock);
    }
  }

  // [Added] Function to transform while loops into `while(true) { if(cond) {...} else {break} }`
  function transformWhileLoop(whileBlock) {
    console.debug(`  -> Transforming while loop: ${whileBlock.id}`);

    const workspace = whileBlock.workspace;
    const mode = whileBlock.getFieldValue('mode');

    // 1. Get original condition and body
    const condAInput = whileBlock.getInput('a');
    const condBInput = whileBlock.getInput('b');
    const operator = whileBlock.getFieldValue('operator');
    const doInput = whileBlock.getInput('do');

    const condABlock = condAInput.connection.targetBlock();
    const condBBlock = condBInput.connection.targetBlock();
    const bodyBlock = doInput.connection.targetBlock();

    if (!condABlock || !condBBlock) {
      console.warn("  [Warn] While loop has no condition, skipping transformation.");
      return;
    }

    // Disconnect them from the while loop
    condAInput.connection.disconnect();
    condBInput.connection.disconnect();
    if (bodyBlock) {
        doInput.connection.disconnect();
    }

    // 2. Change loop to `repeat while 100 == 100` (always true)
    const oneBlock1 = workspace.newBlock('num_dec');
    oneBlock1.setFieldValue('100', 'num_text');
    const oneBlock2 = workspace.newBlock('num_dec');
    oneBlock2.setFieldValue('100', 'num_text');

    whileBlock.setFieldValue('eq', 'operator');
    whileBlock.setFieldValue('while', 'mode'); // Force infinite loop
    condAInput.connection.connect(oneBlock1.outputConnection);
    condBInput.connection.connect(oneBlock2.outputConnection);

    // 3. Create `if-else` block
    const ifBlock = workspace.newBlock('controls_if_custom');
    ifBlock.setFieldValue(operator, 'operator');
    
    // Add an 'else' clause.
    ifBlock.elseCount_ = 1;
    if (ifBlock.updateShape_) {
      ifBlock.updateShape_();
    } else if (!ifBlock.getInput('ELSE')) {
      ifBlock.appendStatementInput('ELSE');
    }

    // 4. Connect original condition to the new if block
    ifBlock.getInput('a').connection.connect(condABlock.outputConnection);
    ifBlock.getInput('b').connection.connect(condBBlock.outputConnection);

    // 5. Connect original body and break based on mode
    const breakBlock = workspace.newBlock('loop_control');
    breakBlock.setFieldValue('break', 'action_sel');

    if (mode === 'until') {
      // until(cond) -> if(cond) break else body
      ifBlock.getInput('do').connection.connect(breakBlock.previousConnection);
      if (bodyBlock) ifBlock.getInput('ELSE').connection.connect(bodyBlock.previousConnection);
    } else {
      // while(cond) -> if(cond) body else break
      if (bodyBlock) ifBlock.getInput('do').connection.connect(bodyBlock.previousConnection);
      ifBlock.getInput('ELSE').connection.connect(breakBlock.previousConnection);
    }

    // 7. Connect the new if-else block to the while loop's body
    doInput.connection.connect(ifBlock.previousConnection);
  }

  // 遞迴處理敘述句 (Statement)
  function processStatement(stmtBlock) {
    if (!stmtBlock) return;

    // [New] Transform while loop
    if (stmtBlock.type === 'controls_whileUntil_ex') {
      transformWhileLoop(stmtBlock);
    }

    // [New] Transform if-elif-else into nested if-else structure.
    if (stmtBlock.type === 'controls_if' || stmtBlock.type === 'controls_if_custom') {
      // [Fix] Check input existence as fallback for elseifCount_
      if (stmtBlock.elseifCount_ > 0 || stmtBlock.getInput('IF1')) {
        transformIfElif(stmtBlock);
      }
    }

    // 檢查該敘述句的所有 Value Input
    stmtBlock.inputList.forEach(input => {
      if (input.type === inputTypes.VALUE) {
        const targetBlock = input.connection.targetBlock();
        
        // [Fix] 嚴格檢查型別相容性，避免 Boolean 運算被錯誤提取到 String 變數中
        const targetConnection = targetBlock ? targetBlock.outputConnection : null;
        const parentConnection = input.connection;
        
        // 1. 來源積木必須能產出 String (因為 set_var 只吃 String)
        const targetCheck = targetConnection ? targetConnection.getCheck() : null;
        const isTargetString = !targetCheck || targetCheck.includes('String');

        // 2. 目標插槽必須能接收 String (因為 get_var 只產出 String)
        const parentCheck = parentConnection ? parentConnection.getCheck() : null;
        const isParentAcceptString = !parentCheck || parentCheck.includes('String');

        // Exception: 如果是 set_var 且來源是常數，則不提取
        const isSetVarConstant = (stmtBlock.type === 'set_var' && isConstant(targetBlock));

        let isSpecialWriteDevice = false;
        if (stmtBlock.type === 'write_device') {
          const devIdHex = stmtBlock.getFieldValue('dev_id');
          if (devIdHex) {
            const devId = parseInt(devIdHex, 16);
            if (devId >= 0xFC) {
              isSpecialWriteDevice = true;
            }
          }
        }
        // 只有當雙方都相容 String 時才提取
        if (targetBlock && !isSimpleValue(targetBlock) && !isSetVarConstant && !isSpecialWriteDevice && isTargetString && isParentAcceptString) {
          if (stmtBlock.type === 'set_var') {
            // [Fix] 如果是 set_var，則不提取頂層指令，只遞迴處理其子節點 (保留 a = cmd 結構)
            console.debug(`[Flatten] Skipping top-level extraction for set_var ${stmtBlock.id}, processing children only.`);
            processExpressionChildren(targetBlock, stmtBlock);
          } else {
            console.debug(`[Flatten] Found complex expression in ${stmtBlock.type} (ID: ${stmtBlock.id}), Input: ${input.name}`);
            extractExpression(targetBlock, stmtBlock, input);
          }
        } else if (targetBlock) {
            // [Fix] 即使不提取當前積木 (例如 Boolean 運算)，仍需遞迴檢查其子節點是否需要提取
            processExpressionChildren(targetBlock, stmtBlock);
        }
      }
      // 如果有子敘述句 (如 IF 的 DO, Loop 的 Body)，遞迴處理
      if (input.type === inputTypes.STATEMENT) {
        const targetBlock = input.connection.targetBlock();
        if (targetBlock) {
          processStatement(targetBlock);
          
          // [Fix] 重新取得該區塊的第一個積木，因為 processStatement 可能在最前面插入了新的 set_var
          const actualStartBlock = input.connection.targetBlock();

          // [Added] Extract to function (skip for procedure definitions)
          if (stmtBlock.type !== 'procedures_defnoreturn' && stmtBlock.type !== 'procedures_defreturn') {
            if (actualStartBlock) {
                extractToFunction(input, actualStartBlock);
            }
          }
        }
      }
    });

    // [New] Release temp variables consumed by this statement
    // This allows reuse of temps like: tmp0 = a+b; x = tmp0; (tmp0 released here)
    releaseTemps(stmtBlock);

    // 繼續處理下一個敘述句
    processStatement(stmtBlock.getNextBlock());
  }

  // 處理運算式的子節點 (遞迴拆解)
  function processExpressionChildren(exprBlock, anchorStmt) {
    exprBlock.inputList.forEach(input => {
      if (input.type === inputTypes.VALUE) { // Check if it's a value input
        const child = input.connection.targetBlock();
        if (child) {
          const targetConnection = child.outputConnection;
          const parentConnection = input.connection;
          const targetCheck = targetConnection ? targetConnection.getCheck() : null;
          const isTargetString = !targetCheck || targetCheck.includes('String');
          const parentCheck = parentConnection ? parentConnection.getCheck() : null;
          const isParentAcceptString = !parentCheck || parentCheck.includes('String');

          if (!isSimpleValue(child) && isTargetString && isParentAcceptString) {
            extractExpression(child, anchorStmt, input);
          } else {
            // Recurse into simple values to check their children
            processExpressionChildren(child, anchorStmt);
          }
        }
      }
    });
  }

  // 提取運算式為暫存變數
  function extractExpression(exprBlock, anchorStmt, parentInput) {
    console.debug(`  -> Extracting ${exprBlock.type} (ID: ${exprBlock.id})`);

    // 1. 先遞迴處理子節點
    processExpressionChildren(exprBlock, anchorStmt);

    // [New] 2. Release temp variables from children after they have been processed
    exprBlock.inputList.forEach(input => {
        if (input.type === inputTypes.VALUE) {
          const child = input.connection.targetBlock();
          if (child && child.type === 'get_var') {
            const variable = tempWs.getVariableById(child.getFieldValue('var'));
            if (variable) {
              tempManager.release({ name: variable.name, id: variable.getId() });
            }
          }
        }
    });

    try {
      // 3. 產生或複用暫存變數
      const tempVarInfo = tempManager.get();
      const variable = tempWs.getVariableById(tempVarInfo.id); // Re-fetch to be safe
      console.debug(`     Allocated temp var: ${tempVarInfo.name} (ID: ${tempVarInfo.id})`);

      // 4. 建立 set_var 積木 (tmp = expr)
      const setBlock = tempWs.newBlock('set_var');
      setBlock.setFieldValue(variable.getId(), 'var');
      
      // 5. 將 exprBlock 移動到 setBlock 的輸入
      console.debug("     Connecting expression to set_var...");
      exprBlock.outputConnection.disconnect();
      setBlock.getInput('data').connection.connect(exprBlock.outputConnection);
      if (!setBlock.getInput('data').connection.isConnected()) {
        throw new Error(`Type mismatch: Cannot connect ${exprBlock.type} to set_var`);
      }
      
      // [Added] If this is a loop condition, clone the set_var block (before connecting it to flow)
      // This ensures the variable is updated at the end of the loop body for the next iteration
      let loopUpdateBlock = null;
      if (isLoopCondition(anchorStmt, parentInput)) {
        const state = Blockly.serialization.blocks.save(setBlock);
        loopUpdateBlock = Blockly.serialization.blocks.append(state, tempWs);
      }

      // 6. 建立 get_var 積木 (取代原本的位置)
      console.debug("     Replacing original expression with get_var...");
      const getBlock = tempWs.newBlock('get_var');
      getBlock.setFieldValue(variable.getId(), 'var');
      parentInput.connection.connect(getBlock.outputConnection);
      if (!parentInput.connection.isConnected()) {
        throw new Error(`Type mismatch: Cannot connect get_var to ${anchorStmt.type} input ${parentInput.name}`);
      }

      // 7. 將 setBlock 插入到 anchorStmt 之前
      console.debug("     Inserting set_var before anchor statement...");
      const prevConn = anchorStmt.previousConnection;
      if (prevConn) {
        if (prevConn.isConnected()) {
          const parentConn = prevConn.targetConnection;
          prevConn.disconnect();
          setBlock.previousConnection.connect(parentConn);
        }
        setBlock.nextConnection.connect(prevConn);
      } else {
        console.warn("     [Warn] Anchor statement has no previous connection!");
      }

      // [Added] Append the cloned update block to the end of the loop body
      if (loopUpdateBlock) {
        console.debug("     [Loop] Appending condition update to loop body...");
        const loopInput = anchorStmt.getInput('do') || anchorStmt.getInput('DO');
        let isConnected = false;
        if (loopInput) {
          const connection = loopInput.connection;
          if (connection.targetBlock()) {
            let lastBlock = connection.targetBlock();
            while (lastBlock.getNextBlock()) {
              lastBlock = lastBlock.getNextBlock();
            }
            if (lastBlock.nextConnection) {
              lastBlock.nextConnection.connect(loopUpdateBlock.previousConnection);
              isConnected = true;
            }
          } else {
            connection.connect(loopUpdateBlock.previousConnection);
            isConnected = true;
          }
        }
        
        if (!isConnected) {
          loopUpdateBlock.dispose();
        }
      }
    } catch (err) {
        console.error("     [Error] in extractExpression:", err);
        throw err;
    }
  }
  
  // 從 Top Blocks 開始遍歷
  console.debug("Processing Top Blocks...\n");
  const topBlocks = tempWs.getTopBlocks(true);
  topBlocks.forEach(block => {
    if (block.type === 'startup') {
      processStatement(block.getInputTargetBlock('statements'));
    }else if (block.type === 'int_task') {
      processStatement(block.getInputTargetBlock('STACK'));
    } else {
      processStatement(block);
    }
  });

  console.log("=== flattenWorkspace End ===\n");
  // 匯出修改後的 State
  const result = Blockly.serialization.workspaces.save(tempWs);
  tempWs.dispose();
  return result;
}
