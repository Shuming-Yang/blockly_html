# parse_mgr.py
"""
[模組] PARSE BLOCKLY JSON

Author: OVT AE
Date: 2026-01-07
Description:
"""
from tkinter import messagebox
from datetime import datetime


class BlocklyConfig:
    """Configuration class: manages command codes, operator mappings, and constants (separates configuration from business logic)"""
    # Command code mapping
    CMD_MAP = {
        "startup": "1202",
        "procedures_defnoreturn": "1202",
        "end": "1201 0f",
        "set_var": "1207",
        "controls_if": "1209",
        "controls_repeat_ext_ex": "120a",  # 0x120a
        "delay": "120e",
        "read_device": "1210",
        "write_device": "1211",
        "print": "1215",
        "procedures_callnoreturn": "1203",
        "abort": "1204",
        "compare_ex": "1208",
        "var_op": "1208",
        "wait_until_timeout_sof": "1214",
        "wait_until_timeout_fsin": "1219",
        "controls_whileUntil_ex": "120a",
        "random_int": "120d",
        "mcu_gpio": "1007",
        "mipi_monitor": "1212",
        "get_mipi_error": "1213",
    }

    # Bitwise operation opcode mapping
    VAR_OP_MAP = {
        "add": "00",
        "sub": "01",
        "mul": "02",
        "div": "03",
        "mod": "05",
        "and": "06",
        "or": "07",
        "xor": "08",
        "lshift": "09",
        "rshift": "0A",
        "eq": "0B",
        "neq": "0C",
        "lt": "0D",
        "lte": "0E",
        "gt": "0F",
        "gte": "10"
    }

    # gpio mapping
    MCU_GPIO_MAP = {
        "gpio_led5": 9,  # not support
        "gpio4": 0,
        "gpio5": 9,  # not support
        "gpio6": 9,  # not support
        "gpio7": 1,
    }


class BlocklyJsonParser:
    """JSON parser: parses JSON and produces structured block node data (decoupled from instruction generation)"""
    def __init__(self, data):
        self.var_addr_map: dict[str, dict] = {}  # variable ID -> {name, addr}
        self.root_blocks: list[dict] = []        # root block node list
        self.gvint = "0"

        # Initialize parsing
        self._parse_obj(data)

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        # %f 會顯示 6 位數的微秒
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"[{ts}][{'PARSEMGR':>16}] [BlocklyJsonParser] {message}")

    def _parse_obj(self, data):
        # 1. Parse variables and assign addresses
        self._parse_variables(data.get("variables", []))

        # 2. Parse root block nodes
        self.root_blocks = data.get("Blocks", [])

    def _parse_variables(self, variables: list[dict]):
        """Parse variable list and generate variable address mapping"""
        variables.insert(0, {"id": "sys1", "orgname": "sys_use1", "name": "sys1"})  # _get_var_index shift++
        variables.insert(0, {"id": "sys0", "orgname": "sys_use0", "name": "sys0"})  # _get_var_index shift++
        for idx, var in enumerate(variables):
            var_id = var.get("name", var["id"])
            var_name = var["orgname"]
            self.var_addr_map[var_id] = {
                "name": var_name,
                "addr": f"{(idx):02x}"  # address as two-digit hexadecimal
            }

    def get_var_addr(self, var_id: str) -> str:
        """Get address by variable ID (utility method)"""
        result = var_id.lstrip("${").rstrip("}")
        return self.var_addr_map.get(result, {}).get("addr", "ff")

    def get_var_name(self, var_id: str) -> str:
        """Get variable name by variable ID (utility method)"""
        items = list(self.var_addr_map.values())[int(var_id)]
        return items.get('name')

    def update_gvint(self, new_vint: str):
        """Update VINT value (only update if changed)"""
        if new_vint != self.gvint:
            self.gvint = new_vint
            return True
        return False


class BlocklyInstructionGenerator:
    """Instruction generator: generates instructions from parsed blocks (decoupled from JSON parsing)"""
    def __init__(self, parser: BlocklyJsonParser, work_path: str):
        self.parser = parser  # holds parser instance (dependency injection)
        self.instruction_list: list[str] = []  # final instruction list
        self.subfunc: dict[str, dict] = {}  # sub-function mapping
        self.subfunc_count: int = 0  # sub-function counter
        self.config = BlocklyConfig  # configuration reference
        self.istravling: int = 0  # flag to indicate if currently traversing
        self._project_path = work_path
        self.occurs_error: int = 0

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        # %f 會顯示 6 位數的微秒
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"[{ts}][{'PARSEMGR':>16}] [BlocklyInstructionGenerator] {message}")

    def _get_var_index(self, var_str: str) -> str:
        shift = 2  # fisrt 2 variable are reserved for system usage in _parse_variables
        val = "".join(filter(str.isdigit, var_str))
        return str(int(val) + shift)

    def generate_instructions(self) -> list[str]:
        """Generate the full instruction sequence (entry method)"""
        # 1. Generate variable mapping comments
        self._generate_var_comment()
        self._generate_procedures_list()
        self.instruction_list.append("FC 1201 00 ;start script")
        self.subfunc_count = 0
        self.occurs_error = 0
        for block in self.parser.root_blocks:
            if block.get("type") == "procedures_defnoreturn":
                self._traverse_block_def_func(block)
                self.subfunc_count += 1
        # 2. Traverse root blocks
        for block in self.parser.root_blocks:
            if block.get("type") == "startup":
                self._traverse_block(block)
        # 3. Append end instruction
        self.instruction_list.append(f"FC {self.config.CMD_MAP['end']}; End SCRIPT")
        return self.instruction_list

    def _generate_procedures_list(self):
        for block in self.parser.root_blocks:
            func_name = block.get("name", "")
            vid = block.get("id", {})
            if vid not in self.subfunc:
                self.add_subfunction_instructions(vid, func_name)

    def _generate_var_comment(self):
        """Generate variable address mapping comments"""
        self.instruction_list.append("; ==== VAR mapping  ====")
        for var_id, info in self.parser.var_addr_map.items():
            self.instruction_list.append(f"; {info['addr']}==>{info['name']}")
        self.instruction_list.append("; ======================")

    def _traverse_block_def_func(self, block: dict) -> tuple[str, str]:
        """Recursively traverse block nodes (core: handle next relationships; returns instruction fragment and comment)"""
        if not block:
            self._log("Debug: Empty block encountered during traversal.")
            return "", ""
        block_type = block.get("type")
        current_instruction = ""
        if block_type == "procedures_defnoreturn":
            current_instruction, _ = self._handle_procedures_defnoreturn(block)
        if current_instruction:
            self.instruction_list.append(f"{current_instruction}")
        return current_instruction, ""

    def _traverse_block(self, block: dict) -> tuple[str, str]:
        """Recursively traverse block nodes (core: handle next relationships; returns instruction fragment and comment)"""
        if not block:
            self._log("Debug: Empty block encountered during traversal.")
            return "", ""
        block_type = block.get("type")
        current_instruction = ""
        block_comment = ""
        # Generate instructions by block type
        if block_type == "startup":
            current_instruction, block_comment = self._handle_startup(block)
        # elif block_type == "procedures_defnoreturn":
        #    current_instruction, block_comment = self._handle_procedures_defnoreturn(block)
        elif block_type == "set_var":
            current_instruction, block_comment = self._handle_set_var(block)
        elif block_type == "get_var":
            current_instruction, block_comment = self._handle_get_var(block)
        elif block_type == "num_dec":
            current_instruction, block_comment = self._handle_num_dec(block)
        elif block_type == "num_hex":
            current_instruction, block_comment = self._handle_num_hex(block)
        elif ((block_type == "var_bitwise") or (block_type == "var_operation")):
            current_instruction, block_comment = self._handle_var_op(block)
        elif block_type == "compare_ex":
            current_instruction, block_comment = self._handle_compare_ex(block)
        elif block_type == "controls_if_custom":
            current_instruction, block_comment = self._handle_controls_if(block)
        elif block_type == "delay":
            current_instruction, block_comment = self._handle_delay(block)
        elif block_type == "read_device":
            current_instruction, block_comment = self._handle_read_device(block)
        elif block_type == "write_device":
            current_instruction, block_comment = self._handle_write_device(block)
        elif block_type == "print":
            current_instruction, block_comment = self._handle_print(block)
        elif block_type == "controls_whileUntil_ex":
            current_instruction, block_comment = self._handle_controls_while_ex(block)
        elif block_type == "controls_repeat_ext_ex":
            current_instruction, block_comment = self._handle_controls_repeat_ext_ex(block)
        elif block_type == "loop_control":
            current_instruction, block_comment = self._handle_loop_control(block)
        elif block_type == "wait_until_timeout":
            current_instruction, block_comment = self._handle_wait_until_timeout(block)
        elif block_type == "procedures_callnoreturn":
            current_instruction, block_comment = self._handle_call_function(block)
        elif block_type == "random_int":
            current_instruction, block_comment = self._handle_random_int(block)
        elif block_type == "mcu_gpio":
            current_instruction, block_comment = self._handle_mcu_gpio(block)
        elif block_type == "abort":
            current_instruction, block_comment = self._handle_abort(block)
        elif block_type == "run_txt":
            current_instruction, block_comment = self._handle_run_txt(block)
        elif (block_type == "emb_mcu") or (block_type == "emb"):
            current_instruction, block_comment = self._handle_emb(block)
        elif block_type == "get_platform":
            current_instruction, block_comment = self._handle_get_platform(block)
        elif block_type == "return_void":
            current_instruction, block_comment = self._handle_return(block)
        elif block_type == "mipi_monitor":
            current_instruction, block_comment = self._handle_mipi_monitor(block)
        elif block_type == "get_mipi_error":
            current_instruction, block_comment = self._handle_get_mipi_error(block)
        else:
            # process unknown block types
            current_instruction, block_comment = self._handle_unknown_block(block)
        if current_instruction and self.istravling == 0:
            self.instruction_list.append(f"{current_instruction}")
            # self._log(f"Debug: False append block type '{block_type}' with comment '{block_comment}'")
            # if current_instruction:
        return current_instruction, block_comment

    # ========== Instruction generation logic for each block type ==========
    def _handle_startup(self, block: dict) -> tuple[str, str]:
        """Handle startup block"""
        # Generate startup instructions
        self.instruction_list.append(";====main start =====")
        self.instruction_list.append(f"FC {self.config.CMD_MAP["startup"]} 00 ;main function ")
        self.parser.update_gvint("0")
        # Process child blocks
        statements = block.get("inputs", [])
        if statements:
            for block in statements:
                self._traverse_block(block)
        self.instruction_list.append(f"FC {self.config.CMD_MAP['procedures_defnoreturn']} 0F; end function block")
        self.parser.update_gvint("0")
        return "", "startup"

    def _handle_procedures_defnoreturn(self, block: dict) -> tuple[str, str]:
        """Handle procedure definition block"""
        # Get function name
        func_name = block.get("name", "")
        vid = block.get("id", {})
        index = self.subfunc.get(vid, {}).get('index', 0)
        self.instruction_list.append(f"; ===subfunc {index}: {func_name}=== ")
        self.instruction_list.append(
                 (f"FC {self.config.CMD_MAP['procedures_defnoreturn']}"
                  f" {index:02x}00; define subfunc:"
                  f" {self.subfunc.get(vid, {}).get('name', 'unknown_func')}"))
        # Process child blocks
        statements = block.get("inputs", [])
        if statements:
            for block in statements:
                self._traverse_block(block)
        self.instruction_list.append(f"FC {self.config.CMD_MAP['procedures_defnoreturn']} {index:02x}0F; end function {self.subfunc.get(vid, {}).get('name', 'unknown_func')}")
        # Process child blocks
        return "", "procedures_defnoreturn"

    def _handle_set_var(self, block: dict) -> tuple[str, str]:
        """Handle variable assignment block"""
        # Get variable info
        var_id = block.get("var", "var")
        var_addr = self._get_var_index(var_id)
        val_name = self.parser.get_var_name(var_addr)
        # Get assignment data
        data_block = block.get("inputs", [])
        data_val = "0000"
        data_comment = ""
        dotmp32bitsvar = ""
        if data_block:
            for block in data_block:
                self.istravling += 1
                data_val, data_comment = self._traverse_block(block)
                self.istravling -= 1
        # Determine type code
        if (data_comment == "num"):
            type_code = "00"
            if (len(data_val) > 4):
                data_val = data_val.zfill(8)
                dotmp32bitsvar = (f"FC 1205 {data_val};"
                                  f" set 32bit {data_val} to sys_use0\n")
                type_code = "12"
                data_val = "0000"
                instruction = (f"FC {self.config.CMD_MAP['set_var']} {type_code}{int(var_addr):02X}{data_val};"
                               f" set_var{int(var_addr):02X} ({val_name}) from sys_use0")
                instruction = f"{dotmp32bitsvar}{instruction}"
            else:
                data_val = data_val.zfill(4)
                # Build instruction
                instruction = (f"FC {self.config.CMD_MAP['set_var']} {type_code}{int(var_addr):02X}{data_val};"
                               f" set_var{int(var_addr):02X} ({val_name}) {data_val}")
        elif (data_comment == "read_device"):
            instruction = data_val[:-6] + f"{int(var_addr):02X}" + data_val[-4:] + f"; set_var{var_addr}({val_name}) from dev " + data_val[-4:]
        elif (data_comment == "emb"):
            instruction = data_val[:-6] + f"{int(var_addr):02X}" + data_val[-4:] + f"; set_var{var_addr}({val_name}) from emb"
        elif (data_comment == "get_platform"):
            instruction = data_val[:10] + f"{int(var_addr):02X}" + data_val[12:] + f" to Var{var_addr}({val_name})"
        elif (data_comment == "var_op"):
            instruction = data_val[:8] + f"{int(var_addr):02X}" + data_val[10:] + f" to {var_addr}({val_name})"
        elif (data_comment == "random_int"):
            instruction = data_val[:10] + f"{int(var_addr):02X}" + data_val[12:]
        elif (data_comment == "get_mipi_error"):
            vc_val = int(data_val[12:14], 16)
            instruction = data_val[:10] + f"{int(var_addr):02X}" + data_val[12:] + f"; set_var{var_addr}({val_name}) = MIPI_ERROR(VC{vc_val}), bit[0:freeze, 1:sof, 2:eof, 6:size, 7:crc]"
        elif (data_comment == "get_var"):
            data_val
            instruction = (f"FC 1207 12{int(var_addr):02X}{int(data_val):04X}"
                           f"; set_var{var_addr}({val_name}) = Var{data_val}")
        else:
            type_code = "12"
            instruction = (f"FC 1206============== {data_comment}")
        return instruction, "set_var"

    def _handle_get_var(self, block: dict) -> tuple[str, str]:
        """Handle variable assignment block"""
        # Get variable info
        var_id = block.get("var", "var")
        var_addr = self._get_var_index(var_id)
        instruction = f"{var_addr}"
        return instruction, "get_var"

    def _handle_num_dec(self, block: dict) -> tuple[str, str]:
        """Handle decimal number block"""
        num_val = block.get("num_dec", 0)
        instruction = f"{int(num_val):04x}"
        return instruction, "num"

    def _handle_num_hex(self, block: dict) -> tuple[str, str]:
        """Handle hexadecimal number block"""
        hex_val = block.get("num_hex", "0000")
        instruction = f"{hex_val}"
        return instruction, "num"

    def _handle_var_op(self, block: dict) -> tuple[str, str]:
        """process var_bitwise block"""
        # get operator
        op_type = block.get("op", "unknown")
        op_code = self.config.VAR_OP_MAP.get(op_type, "00")
        data_block = block.get("inputs", [])
        vars_list = [item['var'] for item in data_block]
        in_x = self._get_var_index(vars_list[0])
        in_y = self._get_var_index(vars_list[1])
        in_Rx_name = self.parser.get_var_name(in_x)
        in_Ry_name = self.parser.get_var_name(in_y)
        # connect instruction
        base_cmd = self.config.CMD_MAP["var_op"]
        n = 'FF'
        instruction = (f"FC {base_cmd} {n}{int(in_x):02x}{op_code}{int(in_y):02x};"
                       f" var_op:  {in_Rx_name} {op_type} {in_Ry_name}")
        return instruction, "var_op"

    def _handle_compare_ex(self, block: dict) -> tuple[str, str]:
        instruction = " compare_ex: "
        return instruction, "compare_ex"

    def _handle_controls_if(self, block: dict) -> tuple[str, str]:
        """process if block"""
        # basic instruction
        base_cmd = self.config.CMD_MAP["controls_if"]
        instruction = f"FC {base_cmd}"
        # process IF0
        IF_OP = block.get("op", "")
        if_type = "00"  # only support Rx OP Ry
        if_Rx = "NA"
        if_Ry = "NA"
        if_op_code = self.config.VAR_OP_MAP.get(IF_OP, "00")
        statements = block.get("inputs", [])
        if statements:
            merged = {k: v for d in statements for k, v in d.items()}
            self.istravling += 1
            if_Rx, _ = self._traverse_block(merged.get('a'))
            if_Ry, _ = self._traverse_block(merged.get('b'))
            self.istravling -= 1
            if_Rx_name = self.parser.get_var_name(if_Rx)
            if_Ry_name = self.parser.get_var_name(if_Ry)
            instruction = (f"{instruction} {if_type}{int(if_Rx):02X}{if_op_code}{int(if_Ry):02X};"
                           f" if condition: {if_Rx}({if_Rx_name}) {IF_OP} {if_Ry}({if_Ry_name})")
            # process DO0
            do0_block = merged.get('do')
            if do0_block:
                self.istravling += 1
                do_instr, _ = self._traverse_block(do0_block)
                self.istravling -= 1
                instruction = f"{instruction}\n{do_instr}"
            # process else
            else_block = merged.get('else')
            if else_block:
                do_instr = f"FC {base_cmd} 01000000; else"
                instruction = f"{instruction}\n{do_instr}"
                self.istravling += 1
                do_instr, _ = self._traverse_block(else_block)
                self.istravling -= 1
                instruction = f"{instruction}\n{do_instr}"
        endifinstr = f"FC {base_cmd} 0f000000 ; end if"
        instruction = f"{instruction}\n{endifinstr}"
        return instruction, "controls_if"

    def _handle_delay(self, block: dict) -> tuple[str, str]:
        """process delay block"""
        time = int(block.get("time", 0))
        time_unit = block.get("time_unit", "ms")
        if time_unit == "ms":
            unit_code = "01"
            time_hex = f"{time:08x}"
            instruction = f"FC 1205 {time_hex}\n"
            time_hex = "000000"
        else:
            unit_code = "00"
            instruction = ""
            time_hex = f"{time:06x}"
        # connect instruction
        delay_instr = (f"FC {self.config.CMD_MAP['delay']} {unit_code}{time_hex} ;"
                       f" delay {time}{time_unit}")
        instruction = f"{instruction}{delay_instr}"
        return instruction, "delay"

    def _handle_read_device(self, block: dict) -> tuple[str, str]:
        """process read device block"""
        dev_id = block.get("dev_id", "00")
        address = block.get("addr", "0000")
        length = block.get("length_sel", "01")
        n = "FF"
        # calculate vint
        if dev_id in ("64", "0x64"):
            t = 'F1'
            address = address.zfill(8)
            instruction = f"FC 1205 {address}"
            instruction = f"FC {self.config.CMD_MAP['read_device']} {t}{n}0000"
        else:
            i2ci3c = "00"
            i2cid = dev_id.lstrip("0x") if dev_id.startswith("0x") else dev_id
            i3cid = "00"
            adr_length = len(address) // 2
            dat_length = length
            # update gvint
            vint = f"{i2ci3c}{i2cid}{i3cid}{int(adr_length):01X}{int(dat_length):01X}"
            if self.parser.update_gvint(vint):
                self.instruction_list.append(f"FC 120f {vint}")
            # connect instruction
            if adr_length <= 2:
                t = '00'
                address = address.zfill(4)
                instruction = f"FC {self.config.CMD_MAP['read_device']} {t}{n}{address}"
            else:
                t = '01'
                address = address.zfill(8)
                dotmp32bitsvar = f"FC 1205 {address}\n"
                instruction = f"FC {self.config.CMD_MAP['read_device']} {t}{n}0000"
                instruction = f"{dotmp32bitsvar}{instruction}"
        return instruction, "read_device"

    def _handle_write_device(self, block: dict) -> tuple[str, str]:
        """process write device block"""
        dev_id = block.get("dev_id", "00")
        address = block.get("address", "0000")
        length = block.get("length_sel", "01")
        # get data to write
        data_val = "NA"
        statements = block.get("inputs", [])
        if statements:
           for block in statements:
                self.istravling += 1
                data_val, _ = self._traverse_block(block)
                self.istravling -= 1
        if dev_id in ("64", "0x64"):
            instruction = ((
                f"FC 1205 {address};"
                f" write FPGA adr {address}\n"
                f"FC 1211 F10000{int(data_val):02X};"
                f" write FPGA data from var {data_val}"))
        else:
            i2cid = dev_id.lstrip("0x") if dev_id.startswith("0x") else dev_id
            adr_length = len(address) // 2
            dat_length = length
            # update gvint
            vint = f"00{i2cid}00{int(adr_length):01X}{int(dat_length):01X}"
            if self.parser.update_gvint(vint):
                self.instruction_list.append(f"FC 120f {vint}")
            instruction = ((
                f"FC 1205 {int(address,16):08X};"
                f" write adr {address}\n"
                f"FC 1211 010000{int(data_val):02X};"
                f" write {dev_id} addr {address[-4:]} len {length} data {data_val}"))
        return instruction, "write_device"

    def _handle_print(self, block: dict) -> tuple[str, str]:
        value = block.get("val", "")
        # Prepare display string for comment: escape actual control characters to literals
        display_value = value.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
        # Handle escape sequences (convert literal '\n' to 0x0A, etc.)
        if value:
            value = value.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
        optype = '0'
        if value and value.startswith('$'):
            result = self.parser.get_var_addr(value)
            val_name = self.parser.get_var_name(int(result,16))
            optype = '81' + result.zfill(6)
            option = ""
            value = ""
            display_value = ""
        else:
            val_name = 'String out'
            optype = '07000000'
            option = "FC 1228 0 ; set User str\n"
            s_ascii = value.encode('ascii')

            padding_needed = (4 - len(s_ascii) % 4) % 4
            # 補上 0x00 (\x00)
            data_padded = s_ascii + b'\x00' * padding_needed
            
            hex_list = [
                int.from_bytes(data_padded[i:i+4], byteorder='big') 
                for i in range(0, len(data_padded), 4)
            ]
            result = [f"FC 1229 {x:08X}" for x in hex_list]
            final_string = "\n".join(result)
            option = f"{option}{final_string}\n"
        instruction = (f"FC {self.config.CMD_MAP['print']} {optype}; print {display_value} {val_name}")
        instruction = f"{option}{instruction}"
        return instruction, "print"

    def _handle_controls_while_ex(self, block: dict) -> tuple[str, str]:
        mode = block.get("mode", "WHILE")
        base_cmd = self.config.CMD_MAP["controls_whileUntil_ex"]
        a_var = block.get("a").get("var", "var0")
        nums = self._get_var_index(a_var)
        instruction = (f"FC {base_cmd} 10{int(nums):06X};"
                       f" loop(MODE={mode})")
        do_block = block.get("do")
        self.istravling += 1
        instr, _ = self._traverse_block(do_block)
        instruction = f"{instruction}\n{instr}"
        self.istravling -= 1
        endloopinstr = f"FC {base_cmd} 0f000000 ; end while loop"
        instruction = f"{instruction}\n{endloopinstr}"
        return instruction, "controls_whileUntil_ex"

    def _handle_loop_control(self, block: dict) -> tuple[str, str]:
        """process loop break block """
        base_cmd = self.config.CMD_MAP["controls_repeat_ext_ex"]
        sel = block.get("ctrl", "")
        if sel == 'break':
            instruction = f"FC {base_cmd} 01000000 ; break loop"
        else:
            instruction = f"FC {base_cmd} 02000000 ; Continue loop"
        return instruction, "loop_contrl"

    def _handle_controls_repeat_ext_ex(self, block: dict) -> tuple[str, str]:
        """process controls_repeat_ext_ex block """
        # get repeat count
        repeat_count = block.get("times", 0)
        # change to hex
        repeat_hex = f"{int(repeat_count):08x}"
        base_cmd = self.config.CMD_MAP["controls_repeat_ext_ex"]
        instruction = (f"FC {base_cmd} {repeat_hex};"
                       f" repeat {repeat_count} times (hex:{repeat_hex})")
        # process repeated content
        statements = block.get("inputs", [])
        if statements:
            for do_block in statements:
                self.istravling += 1
                instr, cmts = self._traverse_block(do_block)
                instruction = f"{instruction}\n{instr}"
                self.istravling -= 1

        endloopinstr = f"FC {base_cmd} 0f000000 ; end repeat loop"
        instruction = f"{instruction}\n{endloopinstr}"
        return instruction, "controls_repeat_ext_ex"

    def _handle_wait_until_timeout(self, block: dict) -> tuple[str, str]:
        timeout = block.get("timeout", 0)
        timeout = 'FF' if int(timeout) == '0' else timeout
        timeout_hex = f"{int(timeout):04x}"
        event_sel = block.get("event", "unknowsel")
        flag = '01'
        if event_sel == 'fsin':
            base_cmd = '1219'
        elif event_sel == 'sof':
            base_cmd = '1214'
        else: # eof
            base_cmd = '1214'
            flag = '00'
        # 把result 放Ru[1]
        instruction = (f"FC {base_cmd} {flag}01{timeout_hex};"
                       f" wait until timeout: {timeout}ms (hex:{timeout_hex})")
        statements = block.get("inputs", [])
        if statements:
            merged = {k: v for d in statements for k, v in d.items()}
            do_block = merged.get("f_do")
            tout_block = merged.get("f_tout")
            # Ru[0] 設0, 把result 放Ru[1]
            if do_block or tout_block:
                if (do_block):
                    self.istravling += 1
                    instr_do, cmts = self._traverse_block(do_block)
                    self.istravling -= 1
                    # 這裡回傳 'FC 1203 XX'在XX前加入	8bits source(x)+8bits OP + 8bits source(y) Ru[0] ==(0B) Ru[r]
                    instr_do = f"FC 1205 00000000\nFC 1209 00000B01 ; if wait\n{instr_do}"
                    instruction = f"{instruction}\n{instr_do} func_do"
                else:
                    instruction = f"FC 1205 00000000\nFC 1209 00000B01 ; if wait"

                if (tout_block):
                    self.istravling += 1
                    instr_tout, cmts = self._traverse_block(tout_block)
                    # 這裡回傳 'FC 1203 XX'在XX前加入	8bits source(x)+8bits OP + 8bits source(y) Ru[0] !=(0C) Ru[r]
                    instr_tout =f"FC 1209 01000000 ; else do timeout\n{instr_tout}"
                    instruction = f"{instruction}\n{instr_tout} ;func_timeout"
                    self.istravling -= 1
                instruction = f"{instruction}\nFC 1209 0F000000"
        return instruction, "wait_until_timeout"

    def _handle_call_function(self, block: dict) -> tuple[str, str]:
        func_name = block.get("extraState", {}).get("name", "unknown_call_func")
        func_index = -1
        self.parser.update_gvint("0")  #set gvint 0 fro read device 120F cfg
        for val in self.subfunc.values():
            if val.get('name') == func_name:
                func_index = val['index']
                break
        if func_index == -1:
            messagebox.showerror('Function error', f'No function define')
            self.occurs_error += 1
        self.parser.update_gvint("0")  #set gvint 0 fro read device 120F cfg
        instruction = (f"FC {self.config.CMD_MAP['procedures_callnoreturn']} {func_index:02X};"
                       f" call subfunc: {func_name}")
        return instruction, "procedures_callnoreturn"

    def _handle_random_int(self, block: dict) -> tuple[str, str]:
        _min = block.get("min", 0)
        _max = block.get("max", 10)
        instruction = f"FC {self.config.CMD_MAP['random_int']} 00FF{_min:02X}{_max:02X}; ranRand({_min},{_max})"
        return instruction, "random_int"

    def _handle_return(self, block: dict) -> tuple[str, str]:
        instruction = f"FC 1204 00"
        return instruction, "return"
    
    def _handle_get_platform(self, block: dict) -> tuple[str, str]:
        op = block.get("sel")
        instruction = ""
        if op == "tick_1ms":
            instruction = "FC 1207 04FF0000 ;get tick"
        return instruction, "get_platform"

    def _handle_mcu_gpio(self, block: dict) -> tuple[str, str]:
        gpio = block.get("gpio_sel")
        gpio_val = self.config.MCU_GPIO_MAP[gpio]
        state = block.get("state_sel")
        if state == 'low':
            instruction = f"FC {self.config.CMD_MAP['mcu_gpio']} 4{gpio_val:01X}{0:06X}; set {gpio} {state}"
        elif state == 'high':
            instruction = f"FC {self.config.CMD_MAP['mcu_gpio']} 4{gpio_val:01X}{1:06X}; set {gpio} {state}"
        else:  #  pulse
            if gpio_val == 1:
                pluse = f"55003000"
            else:
                pluse = f"54003000"
            instruction = f"FC {self.config.CMD_MAP['mcu_gpio']} {pluse}; set {gpio} pulse"
        return instruction, "mcu_gpio"

    def is_hex(self, s: str):
        test_str = s.replace(" ", "")
        return all(c in "0123456789ABCDEFabcdef" for c in test_str)

    def _handle_run_txt(self, block: dict) -> tuple[str, str]:
        filename = block.get("txt")
        txt_name = self._project_path + '\\' + filename
        instruction = f"; txt file {filename}\nFC 1217 00"
        try:
            with open(txt_name, 'r', encoding='utf-8') as f:
                for line in f:
                    clean_line = line.strip()
                    clean_line = clean_line.split(';')[0].strip()
                    if not clean_line:
                        continue
                    # 2. 檢查是否以 SL 或 DELAY 開頭
                    is_command = clean_line.upper().startswith(('SL', 'DELAY'))
                    is_hex_data = self.is_hex(clean_line)
                    is_fpga_cmd = clean_line.startswith(('64'))
                    # 過濾邏輯：如果是指令 OR 是純16進位數據
                    if is_command:
                        value = line.split()[1].zfill(6)
                        hex_str = f"{value}"
                        instruction = f"{instruction}\nFC 120E 01{hex_str}"
                    elif is_fpga_cmd:
                        dev, addr, data, *_ = line.split()
                        instruction = f"{instruction}\nFC 1063 {addr}\nFC 1064 {data}"
                    elif is_hex_data:
                        instruction = f"{instruction}\n{line.strip()}"
                    else:
                        continue
        except FileNotFoundError as e:
            messagebox.showerror('run file Error', f'run file {e}')
            self.occurs_error += 1
        instruction = f"{instruction}\nFC 1217 0F\n; end of file{filename}"
        return instruction, "run_txt"

    def _handle_abort(self, block: dict) -> tuple[str, str]:
        instruction = f"FC {self.config.CMD_MAP['abort']} 01; abort"
        return instruction, "abort"

    def _handle_emb(self, block: dict) -> tuple[str, str]:
        offset = block.get("offset")
        vc = block.get("vc_sel")
        instruction = f"FC 1205 FC{int(vc[-1]):02X}{int(offset):04X}; EMB offset"
        readout = "FC 1210 F1FF0000"
        instruction = f"{instruction}\n{readout}"
        return instruction, "emb"

    def _handle_mipi_monitor(self, block: dict) -> tuple[str, str]:
        """process mipi_monitor block"""
        threshold = block.get("threshold", 0)
        mode = 0
        comment_parts = []
        # SOF/EOF Errors
        sof_eof_vcs = []
        if block.get('sof_eof_vc0'):
            mode |= (1 << 0)
            sof_eof_vcs.append('0')
        if block.get('sof_eof_vc1'):
            mode |= (1 << 1)
            sof_eof_vcs.append('1')
        if block.get('sof_eof_vc2'):
            mode |= (1 << 2)
            sof_eof_vcs.append('2')
        if block.get('sof_eof_vc3'):
            mode |= (1 << 3)
            sof_eof_vcs.append('3')
        if sof_eof_vcs:
            comment_parts.append(f"sof_eof_vc=[{','.join(sof_eof_vcs)}]")
        # Size Errors
        size_err_vcs = []
        if block.get('size_err_vc0'):
            mode |= (1 << 4)
            size_err_vcs.append('0')
        if block.get('size_err_vc1'):
            mode |= (1 << 5)
            size_err_vcs.append('1')
        if block.get('size_err_vc2'):
            mode |= (1 << 6)
            size_err_vcs.append('2')
        if block.get('size_err_vc3'):
            mode |= (1 << 7)
            size_err_vcs.append('3')
        if size_err_vcs:
            comment_parts.append(f"size_err_vc=[{','.join(size_err_vcs)}]")
        # CRC Error
        if block.get('crc_err'):
            mode |= (1 << 15)
            comment_parts.append("crc")
        base_cmd = self.config.CMD_MAP["mipi_monitor"]
        threshold_hex = f"{int(threshold):02x}"
        mode_hex = f"{int(mode):04x}"
        comment = f"Monitor MIPI Error: threshold={threshold}"
        if comment_parts:
            comment += ", " + ", ".join(comment_parts)
        instruction = (f"FC {base_cmd} {threshold_hex}{mode_hex}; {comment}")
        return instruction, "mipi_monitor"

    def _handle_get_mipi_error(self, block: dict) -> tuple[str, str]:
        vc_sel = block.get("vc_sel", "vc0")
        vc_map = {"vc0": 0, "vc1": 1, "vc2": 2, "vc3": 3}
        vc_val = vc_map.get(vc_sel, 0)
        # 16bits output(o)+8bits Target(n)+8bits dummy
        payload = f"0000{vc_val:02X}00"
        instruction = f"FC {self.config.CMD_MAP['get_mipi_error']} {payload}"
        return instruction, "get_mipi_error"

    def _handle_unknown_block(self, block: dict) -> tuple[str, str]:
        self._log(f"; Warning: Unmapped block type '{block.get('type')}' encountered.")
        return "", "unknown"

    def add_subfunction_instructions(self, vid, func_name):
        self.subfunc_count += 1
        self.subfunc[vid] = {"name": func_name}
        self.subfunc[vid]["index"] = self.subfunc_count

    def save_to_txt(self, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            for line in self.instruction_list:
                f.write(line + "\n")


class BlocklyCompiler:
    def __init__(self, IR_object: str, work_path):
        self.parser = BlocklyJsonParser(IR_object)
        self.generator = BlocklyInstructionGenerator(self.parser, work_path)

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        # %f 會顯示 6 位數的微秒
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"[{ts}][{'PARSEMGR':>16}] [BLOCKLYCOMPILER] {message}")

    def compile(self) -> list[str]:
        instructions = self.generator.generate_instructions()
        return instructions


class apiParseMgr:
    def __init__(self):
        pass

    def _log(self, message):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        # %f 會顯示 6 位數的微秒
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        print(f"[{ts}][{'APIPARSEMGR':>16}] {message}")

    def parse_txt(self, IR_object, work_path):
        compiler = BlocklyCompiler(IR_object, work_path)
        instructions = compiler.compile()
        if (compiler.generator.occurs_error != 0):
            instructions = None
        else:
            instructions = self._inline_flatten_functions(instructions)
            instructions = self._prepend_titan_config(instructions)
            self._log("Instructions preview (first 5):")
            for i, line in enumerate(instructions[:5]):
                self._log(f"{i+1}. {line}")
        return instructions

    def _prepend_titan_config(self, instructions):
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'resource', 'TITAN_config.txt')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_lines = [line.rstrip() for line in f]
                instructions = config_lines + instructions
            except Exception as e:
                self._log(f"Error reading TITAN_config.txt: {e}")
        return instructions
    
    def _inline_flatten_functions(self, instructions):
        """
        Post-process instructions to inline functions named 'func_flatten_'.
        This reverses the visual flattening done by the frontend.
        """
        if not instructions:
            return instructions

        # Expand multi-line instructions into a flat list of single lines
        flat_instructions = []
        for instr in instructions:
            if instr:
                flat_instructions.extend(instr.split('\n'))
        instructions = flat_instructions

        flatten_bodies = {}  # idx -> {'name': str, 'lines': list}

        # --- Helper functions for parsing instruction strings ---
        def get_func_start_idx(line):
            # Format: FC 1202 XX00; ...
            parts = line.strip().split()
            if len(parts) >= 3 and parts[0] == "FC" and parts[1] == "1202":
                p2 = parts[2].replace(';', '')
                if len(p2) == 4 and p2.endswith("00"):
                    try:
                        return int(p2[:2], 16)
                    except ValueError:
                        pass
            return -1

        def get_func_end_idx(line):
            # Format: FC 1202 XX0F; ...
            parts = line.strip().split()
            if len(parts) >= 3 and parts[0] == "FC" and parts[1] == "1202":
                p2 = parts[2].replace(';', '')
                if len(p2) == 4 and p2.endswith("0F"):
                    try:
                        return int(p2[:2], 16)
                    except ValueError:
                        pass
            return -1

        def get_func_call_info(line):
            # Format: FC 1203 XX; ... or FC 1203 YYYYYYXX; (modified call)
            parts = line.strip().split()
            if len(parts) >= 3 and parts[0] == "FC" and parts[1] == "1203":
                hex_str = parts[2].replace(';', '')
                # The function index is the last byte (2 chars)
                if len(hex_str) >= 2:
                    try:
                        idx = int(hex_str[-2:], 16)
                        modifier = hex_str[:-2] # Capture any prefix (e.g. 000B01)
                        return idx, modifier
                    except ValueError:
                        pass
            return -1, ""

        # --- Pass 1: Collect bodies of flatten functions ---
        curr_idx = -1
        capturing = False
        temp_lines = []
        current_func_name = ""

        for line in instructions:
            start_idx = get_func_start_idx(line)
            if start_idx > 0:  # > 0 means subfunction (0 is startup)
                # Check if it is a flatten function based on comment
                is_flatten = False
                func_name = ""
                if ";" in line:
                    comment = line.split(";", 1)[1]
                    if "func_flatten_" in comment:
                        is_flatten = True
                        if ":" in comment:
                            func_name = comment.split(":", 1)[1].strip()
                        else:
                            func_name = comment.strip()
                
                if is_flatten:
                    curr_idx = start_idx
                    capturing = True
                    temp_lines = []
                    current_func_name = func_name
                    continue  # Don't include the definition line in the body

            if capturing:
                end_idx = get_func_end_idx(line)
                if end_idx == curr_idx:
                    flatten_bodies[curr_idx] = {'name': current_func_name, 'lines': list(temp_lines)}
                    capturing = False
                    curr_idx = -1
                else:
                    temp_lines.append(line)

        # Recursive inlining helper
        def get_inlined_body(lines, parent_modifier=""):
            res = []
            for i, l in enumerate(lines):
                call_idx, inner_modifier = get_func_call_info(l)
                
                # Determine if we need to apply the parent modifier to this line
                # We only apply it to the FIRST line of the inlined block
                current_line_modifier = ""
                if i == 0:
                    current_line_modifier = parent_modifier

                if call_idx > 0 and call_idx in flatten_bodies:
                    # Recursively inline nested flatten calls
                    combined_mod = current_line_modifier + inner_modifier
                    
                    f_data = flatten_bodies[call_idx]
                    f_name = f_data['name']
                    f_lines = f_data['lines']
                    
                    res.append(f"; ===inline {f_name} start===")
                    res.extend(get_inlined_body(f_lines, combined_mod))
                    res.append(f"; ===inline {f_name} end===")
                else:
                    # Normal instruction
                    new_line = l
                    if current_line_modifier:
                        # Apply modifier: insert at index 8
                        # e.g. "FC 1207 1234" -> "FC 1207 <MOD>1234"
                        if len(new_line) >= 8 and new_line.startswith("FC "):
                            new_line = new_line[:8] + current_line_modifier + new_line[8:]
                    res.append(new_line)
            return res

        # --- Pass 2: Reconstruct instructions list ---
        final_instructions = []
        skip = False
        skip_idx = -1

        for line in instructions:
            # 1. Check if we are entering a definition we need to remove
            start_idx = get_func_start_idx(line)
            if start_idx > 0 and start_idx in flatten_bodies:
                skip = True
                skip_idx = start_idx
                # Attempt to remove the preceding comment line (e.g., "; ===subfunc X...")
                if final_instructions:
                    last_line = final_instructions[-1]
                    if "; ===subfunc" in last_line:
                        final_instructions.pop()
                continue
            
            # 2. Skip lines if we are inside a removed definition
            if skip:
                end_idx = get_func_end_idx(line)
                if end_idx == skip_idx:
                    skip = False
                    skip_idx = -1
                continue

            # 3. Check if this is a call to a flatten function
            call_idx, modifier = get_func_call_info(line)
            if call_idx > 0 and call_idx in flatten_bodies:
                # Inline the body instead of the call
                f_data = flatten_bodies[call_idx]
                f_name = f_data['name']
                f_lines = f_data['lines']
                
                final_instructions.append(f"; ===inline {f_name} start===")
                final_instructions.extend(get_inlined_body(f_lines, modifier))
                final_instructions.append(f"; ===inline {f_name} end===")
            else:
                # Keep normal instruction
                final_instructions.append(line)

        return final_instructions


if __name__ == "__main__":
    import json
    JSON_FILE = "PWM_bb_IR.json"
    TXT_FILE = JSON_FILE.replace("_IR.json", "_Parse.json")
    with open(JSON_FILE, 'r', encoding='utf-8') as _json:
        json_data = json.load(_json)

    _compiler = BlocklyCompiler(json_data)
    _instructions = _compiler.compile()

    print(f"Compile finished. Saved to: {TXT_FILE}")
    print(f"Total {len(_instructions)} instructions generated.")

    print("Instructions preview (first 5):")
    for _i, _line in enumerate(_instructions[:5]):
        print(f"{_i+1}. {_line}")

    with open(TXT_FILE, 'w', encoding='utf-8') as _txt:
        for _line in _instructions:
            _txt.write(_line + "\n")
