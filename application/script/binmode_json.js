/**
 * binmode_json.js
 * 將視覺化積木（例如 Google Blockly 產生的 JSON 格式的 Intermediate Representation，簡稱 IR）解析
 * 並轉換成硬體/韌體可以看懂的十六進制位元組陣列 (Byte Arrays)，
 * 最後包裝成一個包含標頭、模式設定與指令列表的完整 JSON 檔案（finalJsonResult）
 * Blockly IR JSON ➔ IRtobinjson_process (迴圈分類) ➔ Sub_Command (打包單步) ➔ process_cmds (分發) ➔ 特定 Handler (產生硬體 Byte 陣列) ➔ 最終組成 finalJsonResult
 */

// 在檔案最開頭，建立 IIFE 結界
(function() {
  /**
   * 將 16 進位字串左邊補零至指定長度，並轉為大寫。
   * @param {string} hex - 原始 16 進位字串
   * @param {number} length - 目標總長度
   * @returns {string} 補齊後的 16 進位大寫字串
   */
  const formatHex = (hex, length) => hex.padStart(length, '0').toUpperCase();

  /**
   * 將 10 進位數字轉換為 16 進位字串，左邊補零至指定長度，並轉為大寫。
   * @param {number} dec - 10 進位數字
   * @param {number} length - 目標總長度
   * @returns {string} 補齊後的 16 進位大寫字串
   */
  const formatDec = (dec, length) => dec.toString(16).padStart(length, '0').toUpperCase();

  /**
   * 將變數 ID 字串 (例如 "var12") 萃取出數字，轉為 16 進位並補齊長度。
   * @param {string} variableId - Blockly 變數 ID 字串
   * @param {number} length - 目標總長度
   * @returns {string} 代表該變數的 16 進位 ID 字串
   */
  const VarSetHex = (variableId, length) => parseInt(variableId.replace(/\D/g, ''), 10).toString(16).toUpperCase().padStart(length, '0');
  let procedureDict = {};
  // 定義邏輯與數學運算子對應到硬體的 Opcode（例如 add 對應 "00"，eq 等於對應 "0B"）

  let INT_TASK_MAP = {
    "sof": "0011",
    "eof": "0015",
    "line": "000D",
    "timer": "000A",
    "fsin": "000B"
  };

  let VAR_OP_MAP = {
    "eq": "00",
    "neq": "01",
    "gt": "02",
    "gte": "03",
    "lte": "04",
    "lt": "05",
  };

  let VAR_MATH_MAP = {
    "add": "00",
    "sub": "01",
    "not": "02",
    "rshift": "03",
    "lshift": "04",
    "mul": "05",
    "div": "06",
    "and": "07",
    "or": "08",
    "xor": "09",
    "mod": "0A",
  };

  // 定義積木類型對應到硬體的基礎 Opcode 例如寫入硬體對應 "0200"
  let CMD_OP_MAP = {
    "write_device": "0200",
    "delay": "0400",
    "set_var": "0200",
    "print": "0808",
    "controls_repeat_ext_ex": "0803",
    "controls_if_custom": "0110",
    "run_txt": "0302",
    "atb_gpio": "0201",
    "wait_until_timeout": "0902",
  };
  
  const findRunTxt = (obj, results = new Set()) => {
    if (!obj || typeof obj !== 'object') return results;
  
    // 如果發現目標 type，將 txt 加入 Set
    if (obj.type === 'run_txt' && obj.txt) {
      results.add(obj.txt);
    }
  
    // 繼續遞迴遍歷所有子屬性 (陣列或物件)
    Object.values(obj).forEach(value => {
      if (typeof value === 'object') {
        findRunTxt(value, results);
      }
    });
  
    return results;
  };
  let uniqueTxtList = [];

  /**
   * 整個解析器的主要入口：將 Blockly IR 轉換為最終的 Binary JSON 格式。
   * @param {Object|Array} Data - 來自 Blockly 匯出的 IR 資料 (包含所有積木)
   * @returns {Object} 最終要傳給硬體或儲存的完整 Binary JSON
   */
  function IRtobinjson_process(Data) {
    console.log("=== json out Start ===");
    // 資料前處理與驗證：確保取得積木陣列
    const blocksArray = Array.isArray(Data) ? Data : (Data.Blocks) || [];
    if (blocksArray.length === 0) {
      console.error("找不到任何積木資料！");
      return;
    }
    // 計算總包數，並篩選出根節點 (主程式 startup 與 自定義函式 procedures)
    const packagelen = blocksArray.length.toString(16).toUpperCase().padStart(4, '0');
    const targetBlocks = blocksArray.filter(block => 
      block.type === 'startup' || block.type === 'procedures_defnoreturn' || block.type === 'int_task'
    );
    let JsonOut = [];
    let group_num = 769; // 769 的 16進位是 0302，用來配發自定義函式的群組 ID
    let subBlock = [];
    // 遍歷所有根節點，將內部流程包裝為獨立的 Package

    //先整理func list
    targetBlocks.forEach(block => {
      if (block.type === "procedures_defnoreturn") {
        const index = parseInt(block.name.split('_').pop());
        const hexSuffix = (index + 1).toString().padStart(2, '0');
        procedureDict[block.name] = `03${hexSuffix}`;
      }
    });
    uniqueTxtList = Array.from(findRunTxt(Data));
    const txtlist = uniqueTxtList.join(';');
    targetBlocks.forEach(rootBlock => {
      let Mode_hex = '';
      // 決定模式碼：主程式固定為 0300，其餘依序遞增 (0301, 0302...)
      if(rootBlock.type === 'startup') {
        Mode_hex = '0300';
      }else if(rootBlock.type === 'int_task') {
        Mode_hex = INT_TASK_MAP[rootBlock.name];
      } else {
        Mode_hex = group_num.toString(16).toUpperCase().padStart(4, '0');
        group_num += 1;
      }
      // 取得該流程內包含的子步驟數量
      const inputCount = (rootBlock.inputs && Array.isArray(rootBlock.inputs)) ? rootBlock.inputs.length : 0;
      subBlock = [];
      // 遍歷並轉換內部所有的指令積木
      if (rootBlock.inputs) {
        for (let key in rootBlock.inputs) {
          const inputContent = rootBlock.inputs[key]; 
          console.log("handle commd", inputContent.type);
          const cmd_Block = Sub_Command(inputContent); // 解析單步指令
          subBlock.push(cmd_Block);
        }
      }
      // 建立並儲存此群組的封包
      const updatedBlock = {
        "nMode": Mode_hex,
        "CmdCnt": inputCount.toString().padStart(4, '0'),
        "TempGrp": rootBlock.name,
        "Command Lists": subBlock
      };
      JsonOut.push(updatedBlock);
    });
    // 套用硬體規範的外層架構，組合出最終 JSON
    const finalJsonResult = {
      "Application Area": {
        "Device Init": {
          "SnrInit": txtlist
        }
      },
      "header": {
        "Crc": "",
        "PkgCnt": packagelen
      },
      "ExtraConfig": {
        "FilePath": "",
        "ExtendGroupsEn": false
      },
      "Package List": JsonOut,
      "Test Case Information": [
          {
              "Description": "",
              "Test Steps": ""
          }
      ],
      "File End": ""
    };
    return finalJsonResult;
  }

  /**
   * 處理單一積木，將其標準化為硬體可讀的指令封包結構。
   * @param {Object} block - 單一 Blockly IR 積木物件
   * @returns {Object} 封裝好的單步指令 JSON 物件
   */
  function Sub_Command(block) {
    // 初始化單步指令的標準模板，填入硬體要求的固定欄位
    const block_data = {        
      "GlobalID": "0002",
      "CmdListId": "",
      "TCId": "0000",
      "Reserved": "0000",
      "SkipReport": "0000",
      "IfCaseGroup": "0000",
      "ElseCaseGroup": "0000"
    };
    // 呼叫路由分發器，取得該積木轉換後的 Opcode (cmdHex) 與 參數陣列 (string)
    const result = process_cmds(block);
    console.log(result.cmdHex, result.string);
    const subBlock = block.inputs && block.inputs[0];
    // 檢查是否包含子積木 (例如 write 裡面包著 get_var)，用來產生 Description
    let subcmd = "";
    if(subBlock){
      subcmd = subBlock.type;
    }
    if (result.if_group !== undefined) {
      block_data.IfCaseGroup = result.if_group;
    }
    if (result.else_group !== undefined) {
      block_data.ElseCaseGroup = result.else_group;
    }
    block_data.CmdType = result.cmdHex;
    block_data.CmdParams = result.string;
    // 組合描述：主動作+子動作
    block_data.Description = block.type + "+" + subcmd;
    return block_data;
  }

  // =======================================================================
  // 以下為指令解析器 (Dispatcher & Handlers)
  // =======================================================================

  // 定義不同積木類型對應的專屬處理函式 (Map 表)
  const BLOCK_HANDLERS = {
    'write_device': (block) => {
      return cmd_write_device(block);
    },
    'set_var': (block) => {
      return cmd_set_var(block);
    },
    'delay': (block) => {
      return cmd_delay(block);
    },
    'controls_if_custom': (block) => {
      return cmd_controls_if_custom(block);
    },
    'run_txt': (block) => {
      return cmd_run_txt(block);
    },
    'print': (block) => {
      return cmd_print(block);
    },
    'controls_repeat_ext_ex': (block) => {
      return cmd_controls_repeat_ext_ex(block);
    },
    'atb_gpio': (block) => {
      return cmd_gpio(block);
    },
    'abort': (block) => {
      return cmd_abort(block);
    },
    'create_timer': (block) => {
      return cmd_create_timer(block);
    },
    'procedures_callnoreturn': (block) => {
      return cmd_procedures_callnoreturn(block);
    },
    'wait_until_timeout': (block) => {
      return cmd_wait_until_timeout(block);
    },
    // 預設行為：只提取 Opcode，無參數
    'default': (block) => {
      const hex = CMD_OP_MAP[block.type];
      console.log(`Checking default for ${block.type}:`, hex); // 除錯用
      return {
        cmdHex: hex || "FFFF", // 如果找不到，給一個預設值
        string: [],
        if_group: "0000",
        else_group: "0000",
      };
    }
  };

  /**
   * 路由分發器：根據積木類型，導向對應的處理函式。
   * @param {Object} block - 欲處理的積木
   * @returns {Object} 包含 {cmdHex, string} 的解析結果
   */
  function process_cmds(block) {
    const handler = BLOCK_HANDLERS[block.type] || BLOCK_HANDLERS['default'];
    return handler(block);
  }

  /**
   * 處理「變數賦值」積木 (set_var)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_set_var(data){
    let out_string = []; // 每次呼叫都產生一個乾淨的空陣列
    // 提取目標變數 ID 與基礎 Opcode
    const subBlock = data.inputs?.[0] ?? null;
    const var_num = VarSetHex(data.var, 2);
    let cmdHex = CMD_OP_MAP[data.type];
    if(subBlock){
      // 根據「賦值的來源」決定封包格式
      if(subBlock.type === 'read_device') {
        // 來源為讀取硬體
        cmdHex = "0104";
        const dev = formatHex(subBlock.dev_id, 2);
        const address = formatHex(subBlock.addr, 8);
        const lenSel = formatHex(subBlock.length_sel, 8);
        out_string = [dev, "00", "00", "00", ...address.match(/.{1,2}/g), ...lenSel.match(/.{1,2}/g), "AA", "00", "00", var_num];
      } else if(subBlock.type === 'get_var') {
        // 來源為取得變數
        cmdHex = "0104";
        const var_in = VarSetHex(subBlock.var, 2);
        out_string = ["48", "00", "00", "00", "AA", "00", "00", var_in, "00", "00", "00", "04", "AA", "00", "00", var_num];
      } else if (subBlock.type === 'num_hex'){
        // 來源為純 16 進位數字
        const lenSel = "00000004"
        const value = formatHex(subBlock.num_hex, 8);
        out_string = ["48", "00", "00", "00", "AA", "00", "00", var_num, ...lenSel.match(/.{1,2}/g), ...value.match(/.{1,2}/g)];
      } else if (subBlock.type === 'num_dec'){
        // 來源為純 10 進位數字
        const lenSel = "00000004"
        const value = formatDec(subBlock.num_dec, 8);
        out_string = ["48", "00", "00", "00", "AA", "00", "00", var_num, ...lenSel.match(/.{1,2}/g), ...value.match(/.{1,2}/g)];
      } else if (subBlock.type === 'var_operation' || subBlock.type === 'var_bitwise'){
        // 來源為純 10 進位數字
        const opHex = VAR_MATH_MAP[subBlock.op] || "00"; 
        const op0_blocks = subBlock.inputs?.[0] ?? null;
        const op1_blocks = subBlock.inputs?.[1] ?? null;
        const var_num = VarSetHex(data.var, 2);
        const op0var_num = VarSetHex(op0_blocks.var, 2);
        const op1var_num = VarSetHex(op1_blocks.var, 2);
        out_string = [ "01", "00", "00", opHex, "AA", "00", "00", op0var_num,"AA", "00", "00", op1var_num, "AA", "00", "00",var_num ];
        cmdHex = "0801";
      } else if (subBlock.type === 'get_platform'){
        // 來源為純 10 進位數字
        cmdHex = "0104";
        const lenSel = "00000004"
        const value = "AA003018"
        out_string = ["48", "00", "00", "00", ...value.match(/.{1,2}/g), ...lenSel.match(/.{1,2}/g), "AA", "00", "00", var_num];
      } else if (subBlock.type === 'emb'){
        // 來源為純 10 進位數字
        cmdHex = "0104";
        const emb_size = formatDec(subBlock.length_sel, 8);
        let base = "";
        if(subBlock.emb_sel === 'top'){
          base = "80240000";
        } else {
          base = "80241000";
        }
        const value = (parseInt(base, 16) + parseInt(subBlock.offset, 16))
                .toString(16)
                .padStart(8, '0')
                .toUpperCase();
        out_string = ["48", "00", "00", "00", ...value.match(/.{1,2}/g), ...emb_size.match(/.{1,2}/g), "AA", "00", "00", var_num];
      } else if (subBlock.type === 'random_int'){
        // 來源為純 10 進位數字
        cmdHex = "0700";
        const min = formatDec(subBlock.min, 4);
        const max = formatDec(subBlock.max, 4);
        out_string = [...min.match(/.{1,2}/g), ...max.match(/.{1,2}/g), "AA", "00", "00", var_num];
      } else {
        // 未知來源防呆
        out_string = ["77", "00"];
      }
    }
    return {cmdHex: cmdHex, string: out_string};
  }

  /**
   * 處理「寫入硬體」積木 (write_device)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_write_device(data){
    let out_string = []; // 每次呼叫都產生一個乾淨的空陣列
    const subBlock = data.inputs && data.inputs[0];
    if(subBlock){
      // 提取硬體目標參數，並格式化為固定長度 Hex
      const dev = formatHex(data.dev_id, 2);
      const address = formatHex(data.address, 8);
      const lenSel = formatHex(data.length_sel, 8);
      // 判斷寫入資料的來源 (目前處理來源為變數)
      if(subBlock.type === 'get_var') {
        const var_num = VarSetHex(subBlock.var, 2);
        const fromVar = "01"; // 01 代表資料來源是變數
        out_string = [dev, "00", "00", fromVar, ...address.match(/.{1,2}/g), ...lenSel.match(/.{1,2}/g), "AA", "00", "00", var_num];
      }
    }
    return {cmdHex: CMD_OP_MAP[data.type], string: out_string};
  }

  /**
   * 處理「延遲等待」積木 (delay)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_delay(data){
    let out_string = []; // 每次呼叫都產生一個乾淨的空陣列
    // 提取時間單位並統一轉換為微秒 (us)
    const unit = data.time_unit;
    let delay_us = data.time;
    if (unit === 'ms') {
      delay_us = delay_us * 1000;
    }
    // 將微秒轉為 8 字元的 Hex，並拆分成 Byte 陣列
    const out = formatDec(delay_us, 8);
    out_string = ["00", "00", "00", "00", "00", "00", "00", "00", ...out.match(/.{1,2}/g)];
    return {cmdHex: CMD_OP_MAP[data.type], string: out_string};
  }

  /**
   * 處理「條件判斷」積木 (controls_if_custom)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_controls_if_custom(data){
    let out_string = []; // 每次呼叫都產生一個乾淨的空陣列
    // 查詢並獲取比較運算子的對應 Opcode (例如 eq -> 0B)
    const opHex = VAR_OP_MAP[data.op] || "00"; 
    // 取得左右兩側的變數節點
    const subBlock_a = data.inputs?.[0] ?? null;
    const subBlock_b = data.inputs?.[1] ?? null;
    const subBlock_do = data.inputs?.[2] ?? null;
    const subBlock_else = data.inputs?.[3] ?? null;
    let if_group_num = "0000";
    let else_group_num = "0000";
    // 若兩側變數存在，將其轉為 Hex ID 並組合條件判斷封包
    if(subBlock_a && subBlock_b){
      const vara = VarSetHex(subBlock_a.a.var, 2);
      const varb = VarSetHex(subBlock_b.b.var, 2);
      out_string = [opHex, "00", "00", "00", "AA", "00", "00", vara || "00", "AA", "00", "00", varb || "00"];
    }
    if(subBlock_do){
      if_group_num = procedureDict[subBlock_do.do.extraState.name];
    }
    if(subBlock_else){
      else_group_num = procedureDict[subBlock_else.else.extraState.name];
    }
    return {cmdHex: CMD_OP_MAP[data.type], string: out_string, if_group: if_group_num, else_group: else_group_num};
  }

  /**
   * 處理積木 (run_txt)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_run_txt(data){
    const index = uniqueTxtList.indexOf(data.txt); 
    let out_string = ["00", "00", "00", formatDec(index, 2)];

    return {cmdHex: CMD_OP_MAP[data.type], string: out_string};
  }

  /**
   * 處理積木 (print)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_print(data){
    let out_string = [];
    if (data.val.startsWith("${")) {
      const match = data.val.match(/\d+/);
      const index = match ? parseInt(match[0]) : 0;
      out_string = ["AA", "00", "00", formatDec(index, 2)];
      return {cmdHex: "0901", string: out_string};
    } else {
      out_string = data.val.split('').map(char => 
        char.charCodeAt(0).toString(16)
      );
      out_string.push("00");
      // 2. 計算需要補足到 4 倍數的數量 (不足 4 bytes 補 00)
      const paddingSize = (4 - (out_string.length % 4)) % 4;
      for (let i = 0; i < paddingSize; i++) {
        out_string.push("00");
      }
      return {cmdHex: "0900", string: out_string};
    }
  }

  /**
   * 處理積木 (repeat_ext_ex)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_controls_repeat_ext_ex(data){
    const subBlock = data.inputs?.[0] ?? null;
    const nMode = procedureDict[subBlock.extraState.name] || "0000";
    const loopcnt = formatDec(data.times, 8);
    let out_string = [...loopcnt.match(/.{1,2}/g), "00", "00", ...nMode.match(/.{1,2}/g)];
    return {cmdHex: CMD_OP_MAP[data.type], string: out_string};
  }

  /**
   * 處理積木 (gpio)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_gpio(data){
    const pin = data.gpio_sel.replace('gpio', '').padStart(2, '0');
    const modeMap = {
      'low':   '00',
      'high':  '01',
      'pulse': '02'
    };
    const mode = modeMap[data.state_sel] || "00";
    let out_string = [pin, mode, "00", "00"];
    return {cmdHex: CMD_OP_MAP[data.type], string: out_string};
  }

  /**
   * 處理積木 (abort)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_abort(data){
    const address = "AA003001";
    const w_size = "00000001";
    const value = "00000001";
    out_string = ["48", "00", "00", "00", ...address.match(/.{1,2}/g), ...w_size.match(/.{1,2}/g), ...value.match(/.{1,2}/g)];
    return {cmdHex: "0200", string: out_string};
  }

  /**
   * 處理積木 (create_timer)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_create_timer(data){
    let delay_ms = data.time;
    // 將微秒轉為 8 字元的 Hex，並拆分成 Byte 陣列
    const out = formatDec(delay_ms, 8);
    out_string = ["00", "00", "00", "00", ...out.match(/.{1,2}/g)];
    return {cmdHex: "0401", string: out_string};
  }

  /**
   * 處理積木 (procedures_callnoreturn)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_procedures_callnoreturn(data){
    const out = procedureDict[data.extraState.name];
    out_string = ["00", "00", ...out.match(/.{1,2}/g)];
    return {cmdHex: "0800", string: out_string};
  }

  /**
   * 處理積木 (wait_until_timeout)。
   * @param {Object} data - 積木資料
   * @returns {Object} {cmdHex, string} 解析結果
   */
  function cmd_wait_until_timeout(data){
    let out_string = []; 
    const subBlock_do = data.inputs?.[0] ?? null;
    const subBlock_tout = data.inputs?.[1] ?? null;
    let if_group_num = "0000";
    let else_group_num = "0000";
    const out = INT_TASK_MAP[data.event];
    let touttime = formatDec(10000, 4);

    if(subBlock_do){
      if_group_num = procedureDict[subBlock_do.f_do.extraState.name];
    }
    if(subBlock_tout){
      else_group_num = procedureDict[subBlock_tout.f_tout.extraState.name];
      touttime = formatDec(Number(data.timeout), 4);
    }
    out_string = [...out.match(/.{1,2}/g), ...touttime.match(/.{1,2}/g)];
    return {cmdHex: "0902", string: out_string, if_group: if_group_num, else_group: else_group_num};
  }
  // ==========================================
  // 在檔案的最後，將要公開的 API 暴露出去
  // ==========================================
  // 將這個主入口函式綁定到全域的 window 物件上
  // 這樣在 index.html 或是其他腳本中，就能合法呼叫它了
  window.IRtobinjson_process = IRtobinjson_process;
// 關閉 IIFE 結界並立即執行
})();
