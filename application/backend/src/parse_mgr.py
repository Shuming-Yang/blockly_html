# parse_mgr.py
"""
[模組] PARSE BLOCKLY JSON

Author: OVT AE
Date: 2026-01-07
Description:
"""
from tkinter import messagebox
import os
import re
from typing import Any, Dict, List, Tuple, Optional
from shared_utils import global_log

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
        "mipi_monitor": "1220",
        "config_mipi": "1212"
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
        "gpio0": 0,
        "gpio1": 1,
        "gpio2": 2,
        "gpio3": 3,
    }


class BlocklyJsonParser:
    """JSON parser: parses JSON and produces structured block node data (decoupled from instruction generation)"""
    def __init__(self, data: Dict[str, Any]):
        self.var_addr_map: Dict[str, Dict[str, str]] = {}  # variable ID -> {name, addr}
        self.root_blocks: List[Dict[str, Any]] = []        # root block node list

        # Initialize parsing
        self._parse_obj(data)

    def _log(self, message: str):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        global_log(tag="PARSEMGR:BJP", message=message)

    def _parse_obj(self, data: Dict[str, Any]):
        # 1. Parse variables and assign addresses
        self._parse_variables(data.get("variables", []))

        # 2. Parse root block nodes
        self.root_blocks = data.get("Blocks", [])

    def _parse_variables(self, variables: List[Dict[str, Any]]):
        """Parse variable list and generate variable address mapping"""
        variables.insert(0, {"id": "sys1", "orgname": "sys_use1", "name": "sys1"})  # _get_var_index shift++
        variables.insert(0, {"id": "sys0", "orgname": "sys_use0", "name": "sys0"})  # _get_var_index shift++
        for idx, var in enumerate(variables):
            var_id = str(var.get("name", var.get("id", "")))
            var_name = str(var.get("orgname", ""))
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
        try:
            # 確保 var_id 是整數索引
            idx = int(var_id)
            items = list(self.var_addr_map.values())
            if 0 <= idx < len(items):
                return items[idx].get('name', 'unknown')
        except ValueError:
            pass
        return "unknown"


class BlocklyInstructionGenerator:
    """Instruction generator: generates instructions from parsed blocks (decoupled from JSON parsing)"""
    def __init__(self, parser: BlocklyJsonParser, work_path: str):
        self.parser = parser  # holds parser instance (dependency injection)
        self.instruction_list: List[str] = []  # final instruction list
        self.subfunc: Dict[str, Dict[str, Any]] = {}  # sub-function mapping
        self.subfunc_count: int = 0  # sub-function counter
        self.config = BlocklyConfig  # configuration reference
        self.istravling: int = 0  # flag to indicate if currently traversing
        self._project_path = work_path
        self.occurs_error: int = 0
        self.gvint = "0"

    def _log(self, message: str):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        global_log(tag="PARSEMGR:BIG", message=message)

    def _check_vint(self, token) -> list:
        new_instructions: List[str] = []
        dev_id, address, value = token
        length = len(value) // 2
        i2ci3c = "00"
        i2cid = f"{int(dev_id, 16) - 1:02X}"
        i3cid = "e0"
        adr_length = len(address) // 2
        try:
            dat_length_int = int(length)
        except ValueError:
            dat_length_int = 1
        vint = f"{i2ci3c}{i2cid}{i3cid}{int(adr_length):01X}{dat_length_int:01X}"
        if self.update_gvint(vint):
            new_instructions.append(f"FC 120f {vint}")
        return new_instructions

    def update_gvint(self, new_vint: str) -> bool:
        """Update VINT value (only update if changed)"""
        if new_vint != self.gvint:
            self.gvint = new_vint
            return True
        return False

    def _get_var_index(self, var_str: str) -> str:
        shift = 2  # fisrt 2 variable are reserved for system usage in _parse_variables
        val = "".join(filter(str.isdigit, var_str))
        if not val:
            return "0"
        return str(int(val) + shift)

    def generate_instructions(self) -> List[str]:
        """Generate the full instruction sequence (entry method)"""
        # 1. Generate variable mapping comments
        self._generate_var_comment()
        self._generate_procedures_list()
        self.instruction_list.append("FC 1201 00 ;start script")
        self.instruction_list.append("FC 1003 00000000")
        self.instruction_list.append("FC 1004 00020103")
        self.instruction_list.append("FC 1011 00000002")
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
            func_name = str(block.get("name", ""))
            vid = str(block.get("id", ""))
            if vid not in self.subfunc:
                self.add_subfunction_instructions(vid, func_name)

    def _generate_var_comment(self):
        """Generate variable address mapping comments"""
        self.instruction_list.append("; ==== VAR mapping  ====")
        for _var_id, info in self.parser.var_addr_map.items():
            self.instruction_list.append(f"; {info['addr']}==>{info['name']}")
        self.instruction_list.append("; ======================")

    def _traverse_block_def_func(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """Recursively traverse block nodes"""
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

    def _traverse_block(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """Recursively traverse block nodes"""
        if not block:
            self._log("Debug: Empty block encountered during traversal.")
            return "", ""
        block_type = block.get("type")
        current_instruction = ""
        block_comment = ""
        # Generate instructions by block type
        if block_type == "startup":
            current_instruction, block_comment = self._handle_startup(block)
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
        elif block_type == "config_mipi":
            current_instruction, block_comment = self._handle_config_mipi(block)
        elif block_type == "config_mipi_dt":
            current_instruction, block_comment = self._handle_config_mipi_dt(block)
        elif block_type == "print_mipi":
            current_instruction, block_comment = self._handle_print_mipi(block)
        else:
            current_instruction, block_comment = self._handle_unknown_block(block)
        if current_instruction and self.istravling == 0:
            if block_type == "run_txt":
                self.instruction_list.extend(current_instruction.splitlines())
            else:
                self.instruction_list.append(f"{current_instruction}")
        return current_instruction, block_comment

    # ========== Instruction generation logic for each block type ==========
    def _handle_startup(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """Handle startup block"""
        self.instruction_list.append(";====main start =====")
        self.instruction_list.append(f"FC {self.config.CMD_MAP['startup']} 00 ;main function ")
        self.update_gvint("0")
        statements = block.get("inputs", [])
        if statements:
            for child_block in statements:
                self._traverse_block(child_block)
        self.instruction_list.append(f"FC {self.config.CMD_MAP['procedures_defnoreturn']} 0F; end function block")
        self.update_gvint("0")
        return "", "startup"

    def _handle_procedures_defnoreturn(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """Handle procedure definition block"""
        func_name = str(block.get("name", ""))
        vid = str(block.get("id", ""))
        index = self.subfunc.get(vid, {}).get('index', 0)
        self.instruction_list.append(f"; ===subfunc {index}: {func_name}=== ")
        self.instruction_list.append(
                    (f"FC {self.config.CMD_MAP['procedures_defnoreturn']}"
                    f" {index:02x}00; define subfunc:"
                    f" {self.subfunc.get(vid, {}).get('name', 'unknown_func')}"))
        statements = block.get("inputs", [])
        if statements:
            for child_block in statements:
                self._traverse_block(child_block)
        self.instruction_list.append(f"FC {self.config.CMD_MAP['procedures_defnoreturn']} {index:02x}0F; end function {self.subfunc.get(vid, {}).get('name', 'unknown_func')}")
        return "", "procedures_defnoreturn"

    def _handle_set_var(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """Handle variable assignment block"""
        var_id = str(block.get("var", "var"))
        var_addr = self._get_var_index(var_id)
        val_name = self.parser.get_var_name(var_addr)
        data_block = block.get("inputs", [])
        data_val = "0000"
        data_comment = ""
        dotmp32bitsvar = ""
        if data_block:
            for child_block in data_block:
                self.istravling += 1
                data_val, data_comment = self._traverse_block(child_block)
                self.istravling -= 1
        if data_comment == "num":
            type_code = "00"
            if len(data_val) > 4:
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
                instruction = (f"FC {self.config.CMD_MAP['set_var']} {type_code}{int(var_addr):02X}{data_val};"
                                f" set_var{int(var_addr):02X} ({val_name}) {data_val}")
        elif data_comment == "read_device":
            instruction = data_val[:-6] + f"{int(var_addr):02X}" + data_val[-4:] + f"; set_var{var_addr}({val_name}) from dev " + data_val[-4:]
        elif data_comment == "emb":
            instruction = data_val[:-6] + f"{int(var_addr):02X}" + data_val[-4:] + f"; set_var{var_addr}({val_name}) from emb"
        elif data_comment == "get_platform":
            instruction = data_val[:10] + f"{int(var_addr):02X}" + data_val[12:] + f" to Var{var_addr}({val_name})"
        elif data_comment == "var_op":
            instruction = data_val[:8] + f"{int(var_addr):02X}" + data_val[10:] + f" to {var_addr}({val_name})"
        elif data_comment == "random_int":
            instruction = data_val[:10] + f"{int(var_addr):02X}" + data_val[12:]
        elif data_comment == "get_var":
            try:
                data_val_int = int(data_val)
            except ValueError:
                data_val_int = 0
            instruction = (f"FC 1207 12{int(var_addr):02X}{data_val_int:04X}"
                            f"; set_var{var_addr}({val_name}) = Var{data_val}")
        else:
            type_code = "12"
            instruction = f"FC 1206============== {data_comment}"
        return instruction, "set_var"

    def _handle_get_var(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """Handle variable assignment block"""
        var_id = str(block.get("var", "var"))
        var_addr = self._get_var_index(var_id)
        instruction = f"{var_addr}"
        return instruction, "get_var"

    def _handle_num_dec(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """Handle decimal number block"""
        num_val = block.get("num_dec", 0)
        try:
            num_int = int(num_val)
        except ValueError:
            num_int = 0
        instruction = f"{num_int:04x}"
        return instruction, "num"

    def _handle_num_hex(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """Handle hexadecimal number block"""
        hex_val = str(block.get("num_hex", "0000"))
        instruction = f"{hex_val}"
        return instruction, "num"

    def _handle_var_op(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """process var_bitwise block"""
        op_type = str(block.get("op", "unknown"))
        op_code = self.config.VAR_OP_MAP.get(op_type, "00")
        data_block = block.get("inputs", [])
        # 安全取得 in_x 和 in_y
        vars_list = [str(item.get('var', '')) for item in data_block]
        var_x = vars_list[0] if len(vars_list) > 0 else ""
        var_y = vars_list[1] if len(vars_list) > 1 else ""
        in_x = self._get_var_index(var_x)
        in_y = self._get_var_index(var_y)
        in_Rx_name = self.parser.get_var_name(in_x)
        in_Ry_name = self.parser.get_var_name(in_y)
        base_cmd = self.config.CMD_MAP["var_op"]
        n = 'FF'
        instruction = (f"FC {base_cmd} {n}{int(in_x):02x}{op_code}{int(in_y):02x};"
                        f" var_op:  {in_Rx_name} {op_type} {in_Ry_name}")
        return instruction, "var_op"

    def _handle_compare_ex(self, _block: Dict[str, Any]) -> Tuple[str, str]:
        instruction = " compare_ex: "
        return instruction, "compare_ex"

    def _handle_controls_if(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """process if block"""
        base_cmd = self.config.CMD_MAP["controls_if"]
        instruction = f"FC {base_cmd}"
        IF_OP = str(block.get("op", ""))
        if_type = "00"
        if_Rx = "NA"
        if_Ry = "NA"
        if_op_code = self.config.VAR_OP_MAP.get(IF_OP, "00")
        statements = block.get("inputs", [])
        if statements:
            merged = {k: v for d in statements for k, v in d.items()}
            # 安全取得 a 和 b 的字典
            a_dict = merged.get('a')
            b_dict = merged.get('b')
            self.istravling += 1
            if a_dict and isinstance(a_dict, dict):
                if_Rx, _ = self._traverse_block(a_dict)
            if b_dict and isinstance(b_dict, dict):
                if_Ry, _ = self._traverse_block(b_dict)
            self.istravling -= 1
            if_Rx_name = self.parser.get_var_name(if_Rx)
            if_Ry_name = self.parser.get_var_name(if_Ry)
            instruction = (
                f"{instruction} {if_type}{int(if_Rx):02X}{if_op_code}{int(if_Ry):02X};"
                f" if condition: {if_Rx}({if_Rx_name}) {IF_OP} {if_Ry}({if_Ry_name})")
            do0_block = merged.get('do')
            if do0_block and isinstance(do0_block, dict):
                self.istravling += 1
                do_instr, _ = self._traverse_block(do0_block)
                self.istravling -= 1
                instruction = f"{instruction}\n{do_instr}"
            else_block = merged.get('else')
            if else_block and isinstance(else_block, dict):
                do_instr = f"FC {base_cmd} 01000000; else"
                instruction = f"{instruction}\n{do_instr}"
                self.istravling += 1
                do_instr, _ = self._traverse_block(else_block)
                self.istravling -= 1
                instruction = f"{instruction}\n{do_instr}"
        endifinstr = f"FC {base_cmd} 0f000000 ; end if"
        instruction = f"{instruction}\n{endifinstr}"
        return instruction, "controls_if"

    def _handle_delay(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """process delay block"""
        try:
            time_val = int(block.get("time", 0))
        except ValueError:
            time_val = 0
        time_unit = str(block.get("time_unit", "ms"))
        if time_unit == "ms":
            unit_code = "01"
            time_hex = f"{time_val:08x}"
            instruction = f"FC 1205 {time_hex}\n"
            time_hex = "000000"
        else:
            unit_code = "00"
            instruction = ""
            time_hex = f"{time_val:06x}"
        delay_instr = (
            f"FC {self.config.CMD_MAP['delay']} {unit_code}{time_hex} ;"
            f" delay {time_val}{time_unit}")
        instruction = f"{instruction}{delay_instr}"
        return instruction, "delay"

    def _handle_read_device(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """process read device block"""
        dev_id = str(block.get("dev_id", "00"))
        address = str(block.get("addr", "0000"))
        length = str(block.get("length_sel", "01"))
        n = "FF"
        if dev_id in ("64", "0x64"):
            t = 'F1'
            address = address.zfill(8)
            instruction = (
                f"FC 1205 {address}\n"
                f"FC {self.config.CMD_MAP['read_device']} {t}{n}0000")
        elif dev_id in ("110"):
            messagebox.showerror('Not support', 'No support read for dev_110')
            self.occurs_error += 1
            instruction = ""
        else:
            i2ci3c = "00"
            i2cid =  f"{int(dev_id, 16):02X}"
            i3cid = "e0"
            adr_length = len(address) // 2
            try:
                dat_length_int = int(length)
            except ValueError:
                dat_length_int = 1
            vint = f"{i2ci3c}{i2cid}{i3cid}{int(adr_length):01X}{dat_length_int:01X}"
            if self.update_gvint(vint):
                self.instruction_list.append(f"FC 120f {vint}")
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

    def _handle_write_device(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """process write device block"""
        dev_id = str(block.get("dev_id", "00"))
        address = str(block.get("address", "0000"))
        length = str(block.get("length_sel", "01"))
        data_val = "NA"
        statements = block.get("inputs", [])
        data_comment = ""
        if statements:
            for child_block in statements:
                self.istravling += 1
                data_val, data_comment = self._traverse_block(child_block)
                self.istravling -= 1
        try:
            dev_int = int(dev_id, 16)
        except ValueError:
            dev_int = 0

        if dev_int > 0xFF:
            if data_comment == 'num':
                try:
                    val_int = int(data_val, 16)
                except ValueError:
                    val_int = 0
                try:
                    pad_chars = int(length) * 2
                except ValueError:
                    pad_chars = 2
                data_padded = f"{val_int:0{pad_chars}X}"
                instruction = f"{dev_id} {address} {data_padded}"
            else:
                messagebox.showerror('Not support', 'Must num when FC write')
                self.occurs_error += 1
                instruction = ''
        elif dev_id in ("FC", "0xFC"):
            instruction = (
                f"FC {address} {data_val};"
                f" write {address} {data_val}")
        elif dev_id in ("64", "0x64"):
            try:
                data_val_int = int(data_val)
            except ValueError:
                data_val_int = 0
            instruction = ((
                f"FC 1205 {address};"
                f" write FPGA adr {address}\n"
                f"FC 1211 F10000{data_val_int:02X};"
                f" write FPGA data from var {data_val_int}"))
        else:
            i2cid = dev_id.lstrip("0x") if dev_id.startswith("0x") else dev_id
            adr_length = len(address) // 2
            try:
                dat_length_int = int(length)
            except ValueError:
                dat_length_int = 1
            vint = f"00{i2cid}e0{int(adr_length):01X}{dat_length_int:01X}"
            if self.update_gvint(vint):
                self.instruction_list.append(f"FC 120f {vint}")
            try:
                addr_int = int(address, 16)
            except ValueError:
                addr_int = 0
            try:
                data_val_int = int(data_val)
            except ValueError:
                data_val_int = 0
            instruction = ((
                f"FC 1205 {addr_int:08X};"
                f" write adr {address}\n"
                f"FC 1211 010000{data_val_int:02X};"
                f" write {dev_id} addr {address[-4:]} len {length} data {data_val}"))
        return instruction, "write_device"

    def _handle_print_err_check(self, _block: Dict[str, Any]) -> Tuple[str, str]:
        instruction = ((
                "FC 1207 11010000; read out Ro[0] to Ru[1] err_cnt\n"
                "FC 120a 10000001; loop err cnt\n"
                "FC 1215 88000000\n"
                "FC 1006 0000001e; delay 30ms\n"
                "FC 120a 0f000000"))
        return instruction, "print_err_check"

    def _handle_print(self, block: Dict[str, Any]) -> Tuple[str, str]:
        value = str(block.get("val", ""))
        display_value = value.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
        if value:
            value = value.replace("\\n", "\n").replace("\\r", "\r").replace("\\t", "\t")
        optype = '0'
        if value == '${all_records}':
            return self._handle_print_err_check(block)
        if value and value.startswith('$'):
            result = self.parser.get_var_addr(value)
            try:
                result_int = int(result, 16)
            except ValueError:
                result_int = 0
            val_name = self.parser.get_var_name(str(result_int))
            optype = '81' + result.zfill(6)
            option = ""
            display_value = ""
        else:
            val_name = 'String out'
            optype = '07000000'
            option = "FC 1228 0 ; set User str\n"
            s_ascii = value.encode('ascii')
            padding_needed = (4 - len(s_ascii) % 4) % 4
            data_padded = s_ascii + b'\x00' * padding_needed
            hex_list = [
                int.from_bytes(data_padded[i:i+4], byteorder='big')
                for i in range(0, len(data_padded), 4)
            ]
            result_list = [f"FC 1229 {x:08X}" for x in hex_list]
            final_string = "\n".join(result_list)
            option = f"{option}{final_string}\n"
        instruction = f"FC {self.config.CMD_MAP['print']} {optype}; print {display_value} {val_name}"
        instruction = f"{option}{instruction}"
        return instruction, "print"

    def _handle_controls_while_ex(self, block: Dict[str, Any]) -> Tuple[str, str]:
        mode = str(block.get("mode", "WHILE"))
        base_cmd = self.config.CMD_MAP["controls_whileUntil_ex"]
        a_dict = block.get("a", {})
        a_var = "var0"
        if isinstance(a_dict, dict):
            a_var = str(a_dict.get("var", "var0"))
        nums = self._get_var_index(a_var)
        try:
            nums_int = int(nums)
        except ValueError:
            nums_int = 0
        instruction = (f"FC {base_cmd} 10{nums_int:06X};"
                        f" loop(MODE={mode})")
        do_block = block.get("do")
        if do_block and isinstance(do_block, dict):
            self.istravling += 1
            instr, _ = self._traverse_block(do_block)
            instruction = f"{instruction}\n{instr}"
            self.istravling -= 1
        endloopinstr = f"FC 1216 02000064; reconfig Rloop\nFC {base_cmd} 0f000000 ; end while loop"
        instruction = f"{instruction}\n{endloopinstr}"
        return instruction, "controls_whileUntil_ex"

    def _handle_loop_control(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """process loop break block """
        base_cmd = self.config.CMD_MAP["controls_repeat_ext_ex"]
        sel = str(block.get("ctrl", ""))
        if sel == 'break':
            instruction = f"FC {base_cmd} 01000000 ; break loop"
        else:
            instruction = f"FC {base_cmd} 02000000 ; Continue loop"
        return instruction, "loop_contrl"

    def _handle_controls_repeat_ext_ex(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """process controls_repeat_ext_ex block """
        try:
            repeat_count = int(block.get("times", 0))
        except ValueError:
            repeat_count = 0
        repeat_hex = f"{repeat_count:08x}"
        base_cmd = self.config.CMD_MAP["controls_repeat_ext_ex"]
        instruction = (f"FC {base_cmd} {repeat_hex};"
                        f" repeat {repeat_count} times (hex:{repeat_hex})")
        statements = block.get("inputs", [])
        if statements:
            for do_block in statements:
                if isinstance(do_block, dict):
                    self.istravling += 1
                    instr, _cmts = self._traverse_block(do_block)
                    instruction = f"{instruction}\n{instr}"
                    self.istravling -= 1
        endloopinstr = f"FC {base_cmd} 0f000000 ; end repeat loop"
        instruction = f"{instruction}\n{endloopinstr}"
        return instruction, "controls_repeat_ext_ex"

    def _handle_wait_until_timeout(self, block: Dict[str, Any]) -> Tuple[str, str]:
        timeout = str(block.get("timeout", "0"))
        timeout = 'FF' if int(timeout) == 0 else timeout
        try:
            timeout_int = int(timeout)
        except ValueError:
            timeout_int = 0
        timeout_hex = f"{timeout_int:04x}"
        event_sel = str(block.get("event", "unknowsel"))
        flag = '01'
        if event_sel == 'fsin':
            base_cmd = '1219'
        elif event_sel == 'sof':
            base_cmd = '1214'
        else:
            base_cmd = '1214'
            flag = '00'
        instruction = (f"FC {base_cmd} {flag}01{timeout_hex};"
                        f" wait {event_sel} until timeout: {timeout}ms (hex:{timeout_hex})")
        statements = block.get("inputs", [])
        if statements:
            merged = {k: v for d in statements for k, v in d.items() if isinstance(d, dict)}
            do_block = merged.get("f_do")
            tout_block = merged.get("f_tout")
            if do_block or tout_block:
                if do_block and isinstance(do_block, dict):
                    self.istravling += 1
                    instr_do, _cmts = self._traverse_block(do_block)
                    self.istravling -= 1
                    instr_do = f"FC 1205 00000000\nFC 1209 00000B01 ; if wait\n{instr_do}"
                    instruction = f"{instruction}\n{instr_do} func_do"
                else:
                    instruction = f"{instruction}\nFC 1205 00000000\nFC 1209 00000B01 ; if wait"
                if tout_block and isinstance(tout_block, dict):
                    self.istravling += 1
                    instr_tout, _cmts = self._traverse_block(tout_block)
                    instr_tout = f"FC 1209 01000000 ; else do timeout\n{instr_tout}"
                    instruction = f"{instruction}\n{instr_tout} ;func_timeout"
                    self.istravling -= 1
                instruction = f"{instruction}\nFC 1209 0F000000"
        return instruction, "wait_until_timeout"

    def _handle_call_function(self, block: Dict[str, Any]) -> Tuple[str, str]:
        extra_state = block.get("extraState", {})
        func_name = "unknown_call_func"
        if isinstance(extra_state, dict):
            func_name = str(extra_state.get("name", "unknown_call_func"))
        func_index = -1
        self.update_gvint("0")
        for val in self.subfunc.values():
            if val.get('name') == func_name:
                func_index = val.get('index', -1)
                break
        if func_index == -1:
            messagebox.showerror('Function error', 'No function define')
            self.occurs_error += 1
        self.update_gvint("0")
        instruction = (f"FC {self.config.CMD_MAP['procedures_callnoreturn']} {func_index:02X};"
                        f" call subfunc: {func_name}")
        return instruction, "procedures_callnoreturn"

    def _handle_random_int(self, block: Dict[str, Any]) -> Tuple[str, str]:
        try:
            _min = int(block.get("min", 0))
            _max = int(block.get("max", 10))
        except ValueError:
            _min = 0
            _max = 10
        instruction = f"FC {self.config.CMD_MAP['random_int']} 00FF{_min:02X}{_max:02X}; ranRand({_min},{_max})"
        return instruction, "random_int"

    def _handle_return(self, _block: Dict[str, Any]) -> Tuple[str, str]:
        instruction = "FC 1204 00"
        return instruction, "return"

    def _handle_get_platform(self, block: Dict[str, Any]) -> Tuple[str, str]:
        op = str(block.get("sel", ""))
        instruction = ""
        if op == "tick_1ms":
            instruction = "FC 1207 04FF0000 ;get tick"
        return instruction, "get_platform"

    def _handle_mcu_gpio(self, block: Dict[str, Any]) -> Tuple[str, str]:
        gpio = str(block.get("gpio_sel", ""))
        gpio_val = self.config.MCU_GPIO_MAP.get(gpio, 9)
        state = str(block.get("state_sel", ""))
        if state == 'low':
            instruction = f"FC {self.config.CMD_MAP['mcu_gpio']} 4{gpio_val:01X}{0:06X}; set {gpio} {state}"
        elif state == 'high':
            instruction = f"FC {self.config.CMD_MAP['mcu_gpio']} 4{gpio_val:01X}{1:06X}; set {gpio} {state}"
        else:
            instruction = f"FC {self.config.CMD_MAP['mcu_gpio']} 5{gpio_val:01X}02007d; set {gpio} pulse"
        return instruction, "mcu_gpio"

    def is_hex(self, s: str) -> bool:
        test_str = s.replace(" ", "")
        return all(c in "0123456789ABCDEFabcdef" for c in test_str)

    def _handle_run_txt(self, block: Dict[str, Any]) -> Tuple[str, str]:
        filename = str(block.get("txt", ""))
        txt_name = os.path.join(self._project_path, filename) if self._project_path else filename
        instruction = f"; txt file {filename}\nFC 1217 00\nFC 1206 10000000\n"
        try:
            with open(txt_name, 'r', encoding='utf-8') as f:
                for line in f:
                    clean_line = line.strip()
                    clean_line = clean_line.split(';')[0].strip()
                    if not clean_line:
                        continue
                    is_command = clean_line.upper().startswith(('SL', 'DELAY'))
                    is_hex_data = self.is_hex(clean_line)
                    if is_command:
                        parts = line.split()
                        if len(parts) > 1:
                            value = parts[1].zfill(6)
                            hex_str = f"{value}"
                            instruction = f"{instruction}\nFC 120E 01{hex_str}"
                    elif is_hex_data:
                        instruction = f"{instruction}\n{line.strip()}"
                    else:
                        continue
        except FileNotFoundError as e:
            messagebox.showerror('run file Error', f'run file {e}')
            self.occurs_error += 1
        instruction = f"{instruction}\nFC 1217 0F\n; end of file{filename}"
        return instruction, "run_txt"

    def _handle_abort(self, _block: Dict[str, Any]) -> Tuple[str, str]:
        instruction = f"FC {self.config.CMD_MAP['abort']} 01; abort"
        return instruction, "abort"

    def _handle_emb(self, block: Dict[str, Any]) -> Tuple[str, str]:
        try:
            offset = int(block.get("offset", 0))
        except ValueError:
            offset = 0
        vc = str(block.get("vc_sel", "0"))
        try:
            vc_val = int(vc[-1])
        except (ValueError, IndexError):
            vc_val = 0
        instruction = f"FC 1205 FC{vc_val:02X}{offset:04X}; EMB offset"
        readout = "FC 1210 F1FF0000"
        instruction = f"{instruction}\n{readout}"
        return instruction, "emb"

    def _handle_print_mipi(self, block: Dict[str, Any]) -> Tuple[str, str]:
        instruction = f"FC {self.config.CMD_MAP['print']} 05000000; print mipi"
        return instruction, "print_mipi"

    def _handle_config_mipi_dt(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """process config_mipi_dt block"""
        stream = str(block.get("stream", ""))
        vc = str(block.get("vc", ""))
        dt = str(block.get("dt", ""))
        instruction = f"FC {self.config.CMD_MAP['config_mipi']} 3{stream}000{vc}{dt}; mipi stream{stream} vc{vc} dt {dt}"
        return instruction, "config_mipi"

    def _handle_config_mipi(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """process config_mipi block"""
        new_instructions = []
        stream = str(block.get("stream", ""))
        hsize = int(block.get("hsize", 0))
        vsize = int(block.get("vsize", 0))
        max = int(block.get("max", 0))
        min = int(block.get("min", 0))
        new_instructions.append("FC 1212 00000000 ;; mipi_error_detect_config: reset settings")
        if hsize != 0:
            new_instructions.append(f"FC {self.config.CMD_MAP['config_mipi']} 1{stream}{hsize:06X}; mipi hsize {hsize}")
        if hsize != 0:
            new_instructions.append(f"FC {self.config.CMD_MAP['config_mipi']} 2{stream}{vsize:06X}; mipi vsize {vsize}")
        if max != 0:
            new_instructions.append(f"FC {self.config.CMD_MAP['config_mipi']} 4{stream}{max:06X}; mipi max {max}")
        if min != 0:
            new_instructions.append(f"FC {self.config.CMD_MAP['config_mipi']} 5{stream}{min:06X}; mipi min {min}")
        instruction = "\n".join(new_instructions)
        return instruction, "config_mipi"

    def _handle_mipi_monitor(self, block: Dict[str, Any]) -> Tuple[str, str]:
        """process mipi_monitor block"""
        value = int(block.get("value", 0))
        instruction = f"FC {self.config.CMD_MAP['mipi_monitor']} {value:08X}; mipi_monitor"
        return instruction, "mipi_monitor"

    def _handle_unknown_block(self, block: Dict[str, Any]) -> Tuple[str, str]:
        self._log(f"; Warning: Unmapped block type '{block.get('type')}' encountered.")
        return "", "unknown"

    def add_subfunction_instructions(self, vid: str, func_name: str):
        self.subfunc_count += 1
        self.subfunc[vid] = {"name": func_name, "index": self.subfunc_count}

    def save_to_txt(self, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            for line in self.instruction_list:
                f.write(line + "\n")


class BlocklyCompiler:
    def __init__(self, IR_object: Dict[str, Any], work_path: str):
        self.parser = BlocklyJsonParser(IR_object)
        self.generator = BlocklyInstructionGenerator(self.parser, work_path)

    def _log(self, message: str):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        global_log(tag="PARSEMGR:BC", message=message)

    def compile(self) -> List[str]:
        instructions = self.generator.generate_instructions()
        return instructions


class apiParseMgr:
    def __init__(self) -> None:
        self.rules: Dict[str, Any] = {'exact': {}, 'data': {}, 'ba': set(), 'comment': set()}

    def _log(self, message: str):
        """
        支援極高精度時間戳記 (含微秒) 的偵錯打印
        """
        global_log(tag="APIPARSEMGR", message=message)

    def parse_txt(self, IR_object: Dict[str, Any], work_path: str) -> Optional[List[str]]:
        self.rules = self._load_ini_rules()
        compiler = BlocklyCompiler(IR_object, work_path)
        instructions = compiler.compile()
        if compiler.generator.occurs_error != 0:
            return None
        instructions_opt = self._apply_ini_rules(instructions)
        if instructions_opt is not None:
            instructions_opt = self._parse_for_write_64(instructions_opt)
            instructions_opt = self._parse_for_dev_read_check(instructions_opt, compiler )
            instructions_opt = self._inline_flatten_functions(instructions_opt)
        return instructions_opt

    def _load_ini_rules(self) -> Dict[str, Any]:
        rules: Dict[str, Any] = {'exact': {}, 'data': {}, 'ba': set(), 'comment': set()}
        ini_path = os.path.join(os.path.dirname(__file__), 'DevVerifyGUI.ini')
        ini_path = os.path.abspath(ini_path)
        if not os.path.exists(ini_path):
            return rules
        try:
            with open(ini_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith(';'):
                        continue
                    parts = line.split(';', 1)
                    key_part = parts[0].strip()
                    val_part = parts[1].strip() if len(parts) > 1 else ""
                    tokens = key_part.split()
                    if len(tokens) < 3:
                        continue
                    t0, t1, t2 = tokens[0], tokens[1], tokens[2]
                    try:
                        k0 = int(t0, 16)
                    except ValueError:
                        k0 = t0.lower()  # type: ignore
                    try:
                        k1 = int(t1, 16)
                    except ValueError:
                        k1 = t1.lower()  # type: ignore
                    if t2 == 'data':
                        rules['data'][(k0, k1)] = val_part
                    elif t2 == 'ba':
                        rules['ba'].add((k0, k1))
                    elif t2 == 'comment':
                        rules['comment'].add((k0))
                    else:
                        try:
                            k2 = int(t2, 16)
                        except ValueError:
                            k2 = t2.lower()  # type: ignore
                        rules['exact'][(k0, k1, k2)] = val_part
        except Exception as e:
            self._log(f"Error loading INI rules: {e}")
        return rules

    def _parse_for_dev_read_check(
        self, instructions: list,
        compiler: "BlocklyCompiler") -> list:
        if not instructions:
            return instructions
        new_instructions: List[str] = []
        for line in instructions:
            if not line:
                continue
            clean_line = line.split(';')[0].strip()
            tokens = clean_line.split()
            if not tokens:
                new_instructions.append(line)
                continue
            try:
                value = int(tokens[0], 16)
                if value % 2 != 0:
                    if value == 0x65:
                        new_instructions.append(f'FC 1205 {tokens[2]};set value to Ru[0]')
                        new_instructions.append('FC 1207 12010000; move value (Ru[0] to Ru[1])')
                        new_instructions.append(f'FC 1205 {tokens[1]};set addr to Ru[0]')
                        if len(tokens) == 2:
                            new_instructions.append('FC 1221 83000001')
                        else:
                            new_instructions.append('FC 1221 03000001')
                    elif value < 0xFC:
                        if compiler:
                            new_instructions.extend(compiler.generator._check_vint(tokens))
                        if len(tokens) == 2:
                            new_instructions.append(f'FC 1221 80{tokens[1]}00')
                        else:
                            new_instructions.append(f'FC 1221 00{tokens[1]}{tokens[2]}')
                    else:
                        new_instructions.append(line)
                else:
                    new_instructions.append(line)
            except Exception:
                new_instructions.append(line)
        return new_instructions

    def _parse_for_write_64(self, instructions: List[str]) -> List[str]:
        if not instructions:
            return instructions
        new_instructions: List[str] = []
        for line in instructions:
            if not line:
                continue
            clean_line = line.split(';')[0].strip()
            parts = line.split(';', 1)
            comment = parts[1].strip() if len(parts) > 1 else ""
            tokens = clean_line.split()
            if clean_line.startswith('64') and len(tokens) >= 3:
                new_instructions.append(f'FC 1063 {tokens[1]} ;{comment}\nFC 1064 {tokens[2]} ;write FPGA {tokens[1]} {tokens[2]}')
            else:
                new_instructions.append(line)
        return new_instructions

    def _convert_110cmd_line(self, line: str) -> str:
        matched = False
        unmanaged_instructions = []
        new_line = ''
        clean_line = line.split(';')[0].strip()
        tokens = clean_line.split()
        if len(tokens) < 3:
            return "error"
        try:
            t0_val = int(tokens[0], 16)
        except ValueError:
            return "error"
        try:
            t1_val = int(tokens[1], 16)
        except ValueError:
            t1_val = tokens[1].lower()  # type: ignore
        try:
            t2_val = int(tokens[2], 16)
        except ValueError:
            t2_val = tokens[2].lower()  # type: ignore
        if (t0_val, t1_val, t2_val) in self.rules['exact']:
            new_line = str(self.rules['exact'][(t0_val, t1_val, t2_val)])
            matched = True
        elif t0_val in self.rules['comment']:
            new_line = f";{line}"
            matched = True
        elif (t0_val, t1_val) in self.rules['data']:
            rule_expr = str(self.rules['data'][(t0_val, t1_val)])
            try:
                data_int = int(tokens[2], 16)
                repl_tokens = rule_expr.split()
                final_parts: List[str] = []
                expr_buffer: List[str] = []
                for rt in repl_tokens:
                    if expr_buffer:
                        expr_buffer.append(rt)
                    elif self._is_simple_hex(rt):
                        final_parts.append(rt)
                    else:
                        expr_buffer.append(rt)
                if expr_buffer:
                    expr_str = " ".join(expr_buffer)
                    val = self._eval_expr(expr_str, data_int)
                    final_parts.append(val)
                new_line = " ".join(final_parts)
                matched = True
            except Exception as e:
                self._log(f"Error: processing data rule for line '{line}': {e}")
        elif (t0_val, t1_val) in self.rules['ba']:
            new_line = "ba"
            matched = True
        if not matched:
            unmanaged_instructions.append(line)
            warning_message = "Found unmanaged instructions with ID > 0xFF:\n\n" + "\n".join(unmanaged_instructions)
            messagebox.showerror("Unmanaged Instructions", warning_message)
            new_line = "error"
        return new_line

    def _apply_ini_rules(self, instructions: List[str]) -> Optional[List[str]]:
        if not instructions:
            return instructions
        new_instructions: List[str] = []
        for line in instructions:
            if not line:
                continue
            clean_line = line.split(';')[0].strip()
            tokens = clean_line.split()
            is_target = False
            if len(tokens) >= 1:
                try:
                    t0_val = int(tokens[0], 16)
                    if t0_val > 0xFF:
                        is_target = True
                except ValueError:
                    pass
            if is_target:
                if len(tokens) >= 3:
                    new_line = self._convert_110cmd_line(line)
                    if new_line == "ba":
                        new_instructions.append("64 700c5120 80")
                        new_instructions.append(line)
                        new_instructions.append("64 700c5120 81")
                    elif new_line == "error":
                        return None
                    else:
                        new_instructions.append(f"{new_line} ;{line}")
            else:
                new_instructions.append(line)
        return new_instructions

    def _is_simple_hex(self, s: str) -> bool:
        if s == 'data':
            return False
        return bool(re.match(r'^[0-9a-fA-F]+$', s))

    def _eval_expr(self, expr_template: str, data_val: int) -> str:
        # 使用 Any 來迴避較舊版 Python 對 re.Match 的嚴格要求
        def replace_hex(match: Any) -> str:
            s = match.group(0)
            if s == 'data':
                return s
            if s.lower().startswith('0x'):
                return s
            return f'0x{s}'
        expr = re.sub(r'\b\w+\b', replace_hex, expr_template)
        local_scope = {'data': data_val}
        try:
            # pylint 會抓出 eval(), 是因為在 Python 中，eval() 擁有執行任何字串作為程式碼的權限.
            # 如果傳入的字串是惡意使用者輸入的(例如 os.system('rm -rf /')), 就會造成嚴重的資安漏洞.
            result = eval(expr, {}, local_scope)  # pylint: disable=eval-used
            return f"{int(result):x}"
        except Exception as e:
            self._log(f"Error: evaluating expression '{expr_template}': {e}")
            return "0000"

    def _inline_flatten_functions(self, instructions: List[str]) -> List[str]:
        """
        Post-process instructions to inline functions named 'func_flatten_'.
        """
        if not instructions:
            return instructions

        flat_instructions: List[str] = []
        for instr in instructions:
            if instr:
                flat_instructions.extend(instr.split('\n'))
        instructions = flat_instructions
        flatten_bodies: Dict[int, Dict[str, Any]] = {}

        def get_func_start_idx(line: str) -> int:
            parts = line.strip().split()
            if len(parts) >= 3 and parts[0] == "FC" and parts[1] == "1202":
                p2 = parts[2].replace(';', '')
                if len(p2) == 4 and p2.endswith("00"):
                    try:
                        return int(p2[:2], 16)
                    except ValueError:
                        pass
            return -1

        def get_func_end_idx(line: str) -> int:
            parts = line.strip().split()
            if len(parts) >= 3 and parts[0] == "FC" and parts[1] == "1202":
                p2 = parts[2].replace(';', '')
                if len(p2) == 4 and p2.endswith("0F"):
                    try:
                        return int(p2[:2], 16)
                    except ValueError:
                        pass
            return -1

        def get_func_call_info(line: str) -> Tuple[int, str]:
            parts = line.strip().split()
            if len(parts) >= 3 and parts[0] == "FC" and parts[1] == "1203":
                hex_str = parts[2].replace(';', '')
                if len(hex_str) >= 2:
                    try:
                        idx = int(hex_str[-2:], 16)
                        modifier = hex_str[:-2]
                        return idx, modifier
                    except ValueError:
                        pass
            return -1, ""

        curr_idx = -1
        capturing = False
        temp_lines: List[str] = []
        current_func_name = ""
        for line in instructions:
            start_idx = get_func_start_idx(line)
            if start_idx > 0:
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
                    continue
            if capturing:
                end_idx = get_func_end_idx(line)
                if end_idx == curr_idx:
                    flatten_bodies[curr_idx] = {'name': current_func_name, 'lines': list(temp_lines)}
                    capturing = False
                    curr_idx = -1
                else:
                    temp_lines.append(line)

        def get_inlined_body(lines: List[str], parent_modifier: str = "") -> List[str]:
            res: List[str] = []
            for i, l in enumerate(lines):
                call_idx, inner_modifier = get_func_call_info(l)
                current_line_modifier = ""
                if i == 0:
                    current_line_modifier = parent_modifier
                if call_idx > 0 and call_idx in flatten_bodies:
                    combined_mod = current_line_modifier + inner_modifier
                    f_data = flatten_bodies[call_idx]
                    f_name = str(f_data['name'])
                    f_lines = f_data['lines']
                    res.append(f"; ===inline {f_name} start===")
                    res.extend(get_inlined_body(f_lines, combined_mod))
                    res.append(f"; ===inline {f_name} end===")
                else:
                    new_line = l
                    if current_line_modifier:
                        if len(new_line) >= 8 and new_line.startswith("FC "):
                            new_line = new_line[:8] + current_line_modifier + new_line[8:]
                    res.append(new_line)
            return res
        final_instructions: List[str] = []
        skip = False
        skip_idx = -1
        for line in instructions:
            start_idx = get_func_start_idx(line)
            if start_idx > 0 and start_idx in flatten_bodies:
                skip = True
                skip_idx = start_idx
                if final_instructions:
                    last_line = final_instructions[-1]
                    if "; ===subfunc" in last_line:
                        final_instructions.pop()
                continue
            if skip:
                end_idx = get_func_end_idx(line)
                if end_idx == skip_idx:
                    skip = False
                    skip_idx = -1
                continue
            call_idx, modifier = get_func_call_info(line)
            if call_idx > 0 and call_idx in flatten_bodies:
                f_data = flatten_bodies[call_idx]
                f_name = str(f_data['name'])
                f_lines = f_data['lines']
                final_instructions.append(f"; ===inline {f_name} start===")
                final_instructions.extend(get_inlined_body(f_lines, modifier))
                final_instructions.append(f"; ===inline {f_name} end===")
            else:
                final_instructions.append(line)
        return final_instructions


if __name__ == "__main__":
    import json
    JSON_FILE = "PWM_bb_IR.json"
    TXT_FILE = JSON_FILE.replace("_IR.json", "_Parse.json")
    with open(JSON_FILE, 'r', encoding='utf-8') as _json:
        json_data = json.load(_json)
    _compiler = BlocklyCompiler(json_data, work_path="")
    _instructions = _compiler.compile()
    print(f"Compile finished. Saved to: {TXT_FILE}")
    print(f"Total {len(_instructions)} instructions generated.")
    print("Instructions preview (first 5):")
    for _i, _line in enumerate(_instructions[:5]):
        print(f"{_i+1}. {_line}")
    with open(TXT_FILE, 'w', encoding='utf-8') as _txt:
        for _line in _instructions:
            _txt.write(_line + "\n")
