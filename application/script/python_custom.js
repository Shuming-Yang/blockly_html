// 定義自訂積木的 Python 生成規則
python.pythonGenerator.forBlock['crc_block'] = function(block, generator) {

  return `print(======Jean)\n`;
};

python.pythonGenerator.forBlock['SCCB'] = function(block, generator) {
  var text_value = block.getFieldValue('addr');
  
  // 組合成 Python 代碼字串
  var code = 'SCCB_R_ADDR_' + text_value ;
  return [code, python.Order.ATOMIC]; 
};

python.pythonGenerator.forBlock['Emb'] = function(block, generator) {
  var text_value = block.getFieldValue('offset');
  
  // 組合成 Python 代碼字串
  var code = 'Emb_offset_' + text_value ;
  return [code, python.Order.ATOMIC]; 
};

// 1. 定義一個通用的生成函式
const commonGenerator = function(block, generator) {
  // 取得函式名稱與參數
  var funcName = generator.getProcedureName(block.getFieldValue('NAME'));
  var branch = generator.statementToCode(block, 'STACK') || '  pass\n';
  var args = [];
  var variables = block.getVars(); // 取得參數變數名
  for (var i = 0; i < variables.length; i++) {
    args.append(generator.getVariableName(variables[i]));
  }
  
  // 組合成 Python 格式
  var code = '\ndef ' + funcName + '(' + args.join(', ') + '):\n' + branch +'\n';
  return code;
};

// 2. 將多個區塊類型映射到這個函式
const blockTypes = ['SOF', 'StartUp', 'Timer'];

blockTypes.forEach(type => {
  python.pythonGenerator.forBlock[type] = commonGenerator;
});

python.pythonGenerator.forBlock['TXT'] = function(block, generator) {
  var text_value = block.getFieldValue('TEXT');
  var code = 'write_txt_file: ' + text_value +'\n';
  
  return code;
};

python.pythonGenerator.forBlock['WSCCB'] = function(block, generator) {
  var text_value = block.getFieldValue('ADDR');
  var wdata_value = block.getFieldValue('WDATA');
  var code = 'write_sccb_Addr ' + text_value + '_valuse_' + wdata_value +'\n';
  
  return code;
};

