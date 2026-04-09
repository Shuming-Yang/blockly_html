// ===================================
// 6. General Utility (Added)
// ===================================
/**
 * 將 flattenWorkspace
 * 目的：解出對印的Test Cmd
 * 產出：Not Ready ==> final output he
 */
let varMap = [];
function IR_generator(obj) {
  const tempWs = new Blockly.Workspace();

  Blockly.serialization.workspaces.load(obj, tempWs);

  // 取得所有積木
  const allBlocks = tempWs.getAllBlocks(false);
  
  // 使用 filter 確保能抓到 startup 以及「所有的」函式定義
  const targetBlocks = allBlocks.filter(block => 
    block.type === 'startup' || block.type === 'procedures_defnoreturn' || block.type === 'int_task'
  );

  const allVariables = tempWs.getAllVariables();

  // 1. 產生帶有新名稱 'var0', 'var1'... 的物件陣列
  const varList = allVariables.map((variable, index) => {
    return {
      id: variable.getId(),
      orgname: variable.name,
      name: `var${index}` // 直接在此處依序改名
    };
  });
  
  // 2. 將陣列轉換成 Map 物件 (Key 是 id, Value 是 name)
  varMap = new Map(varList.map(v => [v.id, v.name]));
  
  let JsonOut = [];
  
  targetBlocks.forEach(rootBlock => {
    // 根據積木類型決定輸入口名稱 (Startup 常見為 statements, 函式固定為 STACK)
    const inputName = (rootBlock.type === 'startup') ? 'statements' : 'STACK';
    // 取得插槽內的第一個子積木
    const firstChild = rootBlock.getInputTargetBlock(inputName);
    const blockObj = {
      type: rootBlock.type,
      id: rootBlock.id,
      name: rootBlock.getFieldValue('NAME') || "NAME"
    };
    if (firstChild) {
      // 執行轉換 (此處會觸發 jsonGenerator.blockToCode)
      const code = jsonGenerator.blockToCode(firstChild);
      
      const finalJsonString = `[\n${code}\n]`;
      const codeSnippet = JSON.parse(finalJsonString);
      // 將結果存入陣列 (假設 codeSnippet 已經是 JSON 格式字串)
      blockObj.inputs = codeSnippet;
    }
    JsonOut.push(blockObj);
  });

  const finalJsonResult = {
    "Blocks": JsonOut,
    "variables": varList
  };

  return finalJsonResult;
}

const jsonGenerator = new Blockly.CodeGenerator('JSON');

jsonGenerator.INDENT = '  ';
jsonGenerator.scrub_ = function(block, code, opt_thisOnly) {
  const nextBlock = block.getNextBlock();
  const nextCode = (nextBlock && !opt_thisOnly) ? this.blockToCode(nextBlock) : '';
  
  if (nextCode) {
    return code + ',\n' + nextCode;
  }
  return code;
};

jsonGenerator.forBlock['startup'] = function(block, generator) {
  const data = {
    type: block.type,
    value: block.type //block.getFieldValue('VALUE')
  };
  return JSON.stringify(data);
};

jsonGenerator.forBlock['set_var'] = function(block, generator) {
  const code = generator.statementToCode(block, 'data'); //inputs
  const varId = block.getFieldValue('var');
  const jsonString = `{
    "type": "${block.type}",
    "var": "${varMap.get(varId)}",
    "inputs": [
      ${code}
    ]
  }`;

  return jsonString;
};

jsonGenerator.forBlock['controls_if_custom'] = function(block, generator) {
  const code_a = generator.statementToCode(block, 'a'); //inputs
  const code_b = generator.statementToCode(block, 'b'); //inputs
  const do_pro = generator.statementToCode(block, 'do'); //inputs
  const else_pro = block.getInput('ELSE') ? generator.statementToCode(block, 'ELSE') : ''; 
  const inputsArray = [];
  if (code_a) inputsArray.push(`{ "a": ${code_a} }`);
  if (code_b) inputsArray.push(`{ "b": ${code_b} }`);
  if (do_pro) inputsArray.push(`{ "do": ${do_pro} }`);
  if (else_pro) inputsArray.push(`{ "else": ${else_pro} }`);
  const jsonString = `{
    "type": "${block.type}",
    "op": "${block.getFieldValue('operator')}",
    "inputs": [
      ${inputsArray.join(',\n    ')}
    ]
  }`;
  return jsonString;
};

jsonGenerator.forBlock['read_device'] = function(block, generator) {
  const data = {
    type: block.type,
    dev_id: block.getFieldValue('dev_id'),
    addr: block.getFieldValue('address'),
    length_sel:block.getFieldValue('length_sel')
  };
  return JSON.stringify(data);
};

jsonGenerator.forBlock['num_hex'] = function(block, generator) {
  const data = {
    type: block.type,
    num_hex: block.getFieldValue('hex_text')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['num_dec'] = function(block, generator) {
  const data = {
    type: block.type,
    num_dec: block.getFieldValue('num_text')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['get_var'] = function(block, generator) {
  // 從積木欄位取得 Variable ID (通常欄位名稱為 'VAR')
  const varId = block.getFieldValue('var');
  const data = {
    type: block.type,
    var: varMap.get(varId),
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['var_bitwise'] = function(block, generator) {
  const code_a = generator.statementToCode(block, 'a'); //inputs
  const code_b = generator.statementToCode(block, 'b'); //inputs
  const jsonString = `{
    "type": "${block.type}",
    "op": "${block.getFieldValue('var_bitwise_operator')}",
    "inputs": [
      ${code_a},
      ${code_b}
    ]
  }`;

  return jsonString;
};

jsonGenerator.forBlock['controls_whileUntil_ex'] = function(block, generator) {
  const code_a = block.getInput('a') ? generator.statementToCode(block, 'a') : ''; 
  const code_b = block.getInput('b') ? generator.statementToCode(block, 'b') : ''; 
  const do_pro = block.getInput('do') ? generator.statementToCode(block, 'do') : ''; 
  const jsonString = `{
    "type": "${block.type}",
    "mode": "${block.getFieldValue('mode')}",
    "op": "${block.getFieldValue('operator')}",
    "a": ${code_a},
    "b": ${code_b},
    "do": ${do_pro}
  }`;

  return jsonString;
};

jsonGenerator.forBlock['controls_repeat_ext_ex'] = function(block, generator) {
  const do_pro = generator.statementToCode(block, 'do'); //inputs
  const jsonString = `{
    "type": "${block.type}",
    "times": "${block.getFieldValue('times')}",
    "inputs": [
      ${do_pro}
    ]
  }`;

  return jsonString;
};

jsonGenerator.forBlock['compare_ex'] = function(block, generator) {
  const code_a = generator.statementToCode(block, 'a'); //inputs
  const code_b = generator.statementToCode(block, 'b'); //inputs
  const inputsArray = [];
  if (code_a) inputsArray.push(`{ "a": ${code_a} }`);
  if (code_b) inputsArray.push(`{ "b": ${code_b} }`);
  const jsonString = `{
    "type": "${block.type}",
    "op": "${block.getFieldValue('operator')}",
    "inputs": [
        ${inputsArray.join(',\n    ')}
    ]
  }`;
  return jsonString;
};

jsonGenerator.forBlock['loop_control'] = function(block, generator) {
  const data = {
    type: block.type,
    ctrl: block.getFieldValue('action_sel')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['random_int'] = function(block, generator) {
  const data = {
    type: block.type,
    min: block.getFieldValue('min'),
    max: block.getFieldValue('max')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['var_operation'] = function(block, generator) {
  const code_a = generator.statementToCode(block, 'a'); //inputs
  const code_b = generator.statementToCode(block, 'b'); //inputs
  const jsonString = `{
    "type": "${block.type}",
    "op": "${block.getFieldValue('var_operator')}",
    "inputs": [
      ${code_a},
      ${code_b}
    ]
  }`;
  return jsonString;
};

jsonGenerator.forBlock['print'] = function(block, generator) {
  const code = generator.valueToCode(block, 'print', 0);
  if (!code) {
    return '';
  }
  try {
    const rawOps = JSON.parse(`[${code}]`);
    const mergedOps = [];
    let currentText = '';

    for (const op of rawOps) {
      if (op.isVar) {
        if (currentText) {
          mergedOps.push({ type: 'print', val: currentText });
          currentText = '';
        }
        mergedOps.push({ type: 'print', val: op.val });
      } else {
        currentText += op.val;
      }
    }

    if (currentText) {
      mergedOps.push({ type: 'print', val: currentText });
    }

    return mergedOps.map(op => JSON.stringify(op)).join(',\n');
  } catch (e) {
    return code;
  }
};

jsonGenerator.forBlock['run_txt'] = function(block, generator) {
  const data = {
    type: block.type,
    txt: block.getFieldValue('path')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['text'] = function(block, generator) {
  const text = block.getFieldValue('text');
  const data = {
    type: 'print',
    val: text,
    isVar: false
  };
  const next = generator.valueToCode(block, 'next_text', 0);
  if (next) {
    return [JSON.stringify(data) + ',\n' + next, 0];
  }
  return [JSON.stringify(data), 0];
};

jsonGenerator.forBlock['newline_text'] = function(block, generator) {
  const data = {
    type: 'print',
    val: '\n',
    isVar: false
  };
  return [JSON.stringify(data), 0];
};

jsonGenerator.forBlock['write_device'] = function(block, generator) {
  const code_a = generator.statementToCode(block, 'data'); //inputs
  const jsonString = `{
    "type": "${block.type}",
    "dev_id": "${block.getFieldValue('dev_id')}",
    "address": "${block.getFieldValue('address')}",
    "length_sel": "${block.getFieldValue('length_sel')}",
    "inputs": [
      ${code_a}
    ]
  }`;

  return jsonString;
};

jsonGenerator.forBlock['get_platform'] = function(block, generator) {
  const data = {
    type: block.type,
    sel: block.getFieldValue('platform_value_sel')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['get_mipi_error'] = function(block, generator) {
  const data = {
    type: block.type,
    vc_sel: block.getFieldValue('vc_sel')
  };
  return JSON.stringify(data);
};


jsonGenerator.forBlock['emb'] = function(block, generator) {
  const data = {
    type: block.type,
    emb_sel: block.getFieldValue('emb_sel'),
    offset: block.getFieldValue('offset'),
    length_sel: block.getFieldValue('length_sel')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['emb_mcu'] = function(block, generator) {
  const data = {
    type: block.type,
    vc_sel: block.getFieldValue('vc_sel'),
    offset: block.getFieldValue('offset')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['wait_until_timeout'] = function(block, generator) {
  const do_pro = generator.statementToCode(block, 'do_func'); //inputs
  const tout_pro = generator.statementToCode(block, 'timeout_func'); //inputs
  const inputsArray = [];
  if (do_pro) inputsArray.push(`{ "f_do": ${do_pro} }`);
  if (tout_pro) inputsArray.push(`{ "f_tout": ${tout_pro} }`);
  const jsonString = `{
    "type": "${block.type}",
    "event": "${block.getFieldValue('event_sel')}",
    "timeout": "${block.getFieldValue('timeout')}",
    "inputs": [
      ${inputsArray.join(',\n    ')}
    ]
  }`;

  return jsonString;
};

jsonGenerator.forBlock['abort'] = function(block, generator) {
  const data = {
    type: block.type
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['mipi_monitor'] = function(block, generator) {
  const data = {
    type: block.type,
    threshold: Number(block.getFieldValue('threshold')),
    sof_eof_vc0: block.getFieldValue('sof_eof_vc0') === 'TRUE',
    sof_eof_vc1: block.getFieldValue('sof_eof_vc1') === 'TRUE',
    sof_eof_vc2: block.getFieldValue('sof_eof_vc2') === 'TRUE',
    sof_eof_vc3: block.getFieldValue('sof_eof_vc3') === 'TRUE',
    size_err_vc0: block.getFieldValue('size_err_vc0') === 'TRUE',
    size_err_vc1: block.getFieldValue('size_err_vc1') === 'TRUE',
    size_err_vc2: block.getFieldValue('size_err_vc2') === 'TRUE',
    size_err_vc3: block.getFieldValue('size_err_vc3') === 'TRUE',
    crc_err: block.getFieldValue('crc_err') === 'TRUE'
  };
  return JSON.stringify(data);
};

jsonGenerator.forBlock['return_void'] = function(block, generator) {
  const data = {
    type: block.type
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['create_timer'] = function(block, generator) {
  const data = {
    type: block.type,
    time: block.getFieldValue('time')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['create_timer_random'] = function(block, generator) {
  const data = {
    type: block.type,
    min: block.getFieldValue('min'),
    max: block.getFieldValue('max')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['timer_active'] = function(block, generator) {
  const data = {
    type: block.type,
    timer_sel: block.getFieldValue('timer_sel'),
    times: block.getFieldValue('times')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['atb_gpio'] = function(block, generator) {
  const data = {
    type: block.type,
    gpio_sel: block.getFieldValue('gpio_sel'),
    state_sel: block.getFieldValue('state_sel')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['mcu_gpio'] = function(block, generator) {
  const data = {
    type: block.type,
    gpio_sel: block.getFieldValue('gpio_sel'),
    state_sel: block.getFieldValue('state_sel')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['delay'] = function(block, generator) {
  const data = {
    type: block.type,
    time: block.getFieldValue('time'),
    time_unit: block.getFieldValue('time_unit')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['variable_text'] = function(block, generator) {
  const varId = block.getFieldValue('var');
  const varName = varMap.get(varId) || 'UNKNOWN';
  const data = {
    type: 'print',
    val: '${' + varName + '}',
    isVar: true
  };
  const next = generator.valueToCode(block, 'next_text', 0);
  if (next) {
    return [JSON.stringify(data) + ',\n' + next, 0];
  }
  return [JSON.stringify(data), 0];
};

jsonGenerator.forBlock['all_records_text'] = function(block, generator) {
  const data = {
    type: 'print',
    val: '${all_records}',
    isVar: true
  };
  return [JSON.stringify(data), 0];
};

jsonGenerator.forBlock['procedures_callnoreturn'] = function(block, generator) {
  const funcName = block.getFieldValue('NAME');
  const data = {
    type: block.type,
    extraState: { name: funcName }
  };
  return JSON.stringify(data); 

};

jsonGenerator.forBlock['config_mipi'] = function(block, generator) {
  const data = {
    type: block.type,
    stream: block.getFieldValue('Stream'),
    hsize: block.getFieldValue('hsize'),
    vsize: block.getFieldValue('vsize'),
    max: block.getFieldValue('ftime_max'),
    min: block.getFieldValue('ftime_min'),
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['config_mipi_dt'] = function(block, generator) {
  const data = {
    type: block.type,
    stream: block.getFieldValue('Stream'),
    vc: block.getFieldValue('VC'),
    dt: block.getFieldValue('DT')
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['mipi_monitor'] = function(block, generator) {
  const bitOrder = [
  'height_err', 'width_err', 'eof_mismatch_err', 'sof_mismatch_err',
  'line_err', 'ecc_err', 'crc_err', 'frame_rate_err0',
  'frame_rate_err1', 'timeout_err', 'vc_dt_err'
  ];
  const finalValue = bitOrder.reduce((acc, key, index) => {
    const isOn = block.getFieldValue(key) === 'TRUE';
    return acc | (isOn ? (1 << index) : 0);
  }, 0);

  const data = {
    type: block.type,
    value: finalValue
  };
  return JSON.stringify(data); 
};

jsonGenerator.forBlock['print_mipi'] = function(block, generator) {
  const data = {
    type: block.type
  };
  return JSON.stringify(data); 
};

