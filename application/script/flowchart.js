/**
 * flowchart.js
 * 負責將 Blockly Workspace JSON 轉換為 Mermaid 流程圖語法
 */

const FlowchartConverter = {
    /**
     * 主入口：轉換整個 Workspace 內容
     */
    convertToMermaid: function(workspace) {
        // 1. 取得 Blockly JSON 狀態
        const state = Blockly.serialization.workspaces.save(workspace);
        
        if (!state.blocks || !state.blocks.blocks) {
            return "graph TD\n  Start((Start)) --> End((Empty Workspace))";
        }

        let mermaidText = "graph TD\n";
        const topBlocks = state.blocks.blocks;

        // 2. 遍歷所有頂層積木（通常從最上面的積木開始）
        topBlocks.forEach(block => {
            mermaidText += this.parseBlock(block);
        });

        return mermaidText;
    },

    /**
     * 遞迴解析個別積木及其後續連線
     */
    parseBlock: function(block) {
        let currentText = "";
        const id = this.cleanId(block.id);
        const label = this.getBlockLabel(block);
        const shape = this.getBlockShape(block);

        // 定義當前節點 (例如: ID[Label])
        currentText += `  ${id}${shape.open}${label}${shape.close}\n`;

        // 3. 處理下一步連線 (Next Statement)
        if (block.next && block.next.block) {
            const nextBlock = block.next.block;
            const nextId = this.cleanId(nextBlock.id);
            
            // 建立連線箭頭
            currentText += `  ${id} --> ${nextId}\n`;
            
            // 遞迴解析下一個積木
            currentText += this.parseBlock(nextBlock);
        }

        return currentText;
    },

    /**
     * 根據積木類型定義標籤文字 (針對您的客製化積木優化)
     */
    getBlockLabel: function(block) {
        switch (block.type) {
            case 'wait_until':
                return `Wait for ${block.fields.event || 'Event'}`;
            case 'SCCB':
                return `SCCB Read\\n(ID: ${block.fields.dev_id}, Addr: ${block.fields.addr})`;
            case 'WSCCB':
                return `SCCB Write\\n(ID: ${block.fields.dev_id}, Addr: ${block.fields.addr})`;
            case 'ATBGPIO':
                return `Set ATB GPIO: ${block.fields.gpio_sel}\\n(State: ${block.fields.len_cfg})`;
            case 'Delay':
                // 假設 Delay 積木內部有 inputs 或 fields
                return `Delay Operation`;
            default:
                // 如果是原生積木或未定義，顯示 type
                return block.type;
        }
    },

    /**
     * 決定流程圖節點形狀
     */
    getBlockShape: function(block) {
        // Mermaid 語法：[] 矩形, {} 菱形, (()) 圓形
        if (block.type === 'controls_if' || block.type === 'compare_ex') {
            return { open: "{", close: "}" }; // 決策菱形
        }
        if (block.type === 'wait_until') {
            return { open: "([", close: "])" }; // 圓角矩形 (等待狀態)
        }
        return { open: "[", close: "]" }; // 一般程序矩形
    },

    /**
     * 清理 ID 字串，確保符合 Mermaid 語法
     */
    cleanId: function(id) {
        return "node_" + id.replace(/[^a-zA-Z0-9]/g, "");
    }
};

// 導出模組（如果使用 ES6 模組）或掛載到 window
window.FlowchartConverter = FlowchartConverter;
