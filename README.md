# Device Verification Tool with Blockly GUI

---

- [Device Verification Tool with Blockly GUI](#device-verification-tool-with-blockly-gui)
- [Project File List](#project-file-list)

---

# Project File List

```txt
LOCAL_blockly_html
├─ application
│  ├─ blockly
│  │  ├─ blockly.min.js
│  │  ├─ blockly.mjs
│  │  ├─ blockly_compressed.js
│  │  ├─ blockly_compressed.js.map
│  │  ├─ blocks.d.ts
│  │  ├─ blocks.js
│  │  ├─ blocks.mjs
│  │  ├─ blocks_compressed.js
│  │  ├─ blocks_compressed.js.map
│  │  ├─ core
│  │  │  ├─ any_aliases.d.ts
│  │  │  ├─ block.d.ts
│  │  │  ├─ blockly.d.ts
│  │  │  ├─ blockly_options.d.ts
│  │  │  ├─ blocks.d.ts
│  │  │  ├─ block_animations.d.ts
│  │  │  ├─ block_flyout_inflater.d.ts
│  │  │  ├─ block_svg.d.ts
│  │  │  ├─ browser_events.d.ts
│  │  │  ├─ bubbles
│  │  │  │  ├─ bubble.d.ts
│  │  │  │  ├─ mini_workspace_bubble.d.ts
│  │  │  │  ├─ textinput_bubble.d.ts
│  │  │  │  └─ text_bubble.d.ts
│  │  │  ├─ bubbles.d.ts
│  │  │  ├─ bump_objects.d.ts
│  │  │  ├─ button_flyout_inflater.d.ts
│  │  │  ├─ clipboard
│  │  │  │  ├─ block_paster.d.ts
│  │  │  │  ├─ registry.d.ts
│  │  │  │  └─ workspace_comment_paster.d.ts
│  │  │  ├─ clipboard.d.ts
│  │  │  ├─ comments
│  │  │  │  ├─ collapse_comment_bar_button.d.ts
│  │  │  │  ├─ comment_bar_button.d.ts
│  │  │  │  ├─ comment_editor.d.ts
│  │  │  │  ├─ comment_view.d.ts
│  │  │  │  ├─ delete_comment_bar_button.d.ts
│  │  │  │  ├─ rendered_workspace_comment.d.ts
│  │  │  │  └─ workspace_comment.d.ts
│  │  │  ├─ comments.d.ts
│  │  │  ├─ common.d.ts
│  │  │  ├─ component_manager.d.ts
│  │  │  ├─ config.d.ts
│  │  │  ├─ connection.d.ts
│  │  │  ├─ connection_checker.d.ts
│  │  │  ├─ connection_db.d.ts
│  │  │  ├─ connection_type.d.ts
│  │  │  ├─ constants.d.ts
│  │  │  ├─ contextmenu.d.ts
│  │  │  ├─ contextmenu_items.d.ts
│  │  │  ├─ contextmenu_registry.d.ts
│  │  │  ├─ css.d.ts
│  │  │  ├─ delete_area.d.ts
│  │  │  ├─ dialog.d.ts
│  │  │  ├─ dragging
│  │  │  │  ├─ block_drag_strategy.d.ts
│  │  │  │  ├─ bubble_drag_strategy.d.ts
│  │  │  │  ├─ comment_drag_strategy.d.ts
│  │  │  │  └─ dragger.d.ts
│  │  │  ├─ dragging.d.ts
│  │  │  ├─ drag_target.d.ts
│  │  │  ├─ dropdowndiv.d.ts
│  │  │  ├─ events
│  │  │  │  ├─ events.d.ts
│  │  │  │  ├─ events_abstract.d.ts
│  │  │  │  ├─ events_block_base.d.ts
│  │  │  │  ├─ events_block_change.d.ts
│  │  │  │  ├─ events_block_create.d.ts
│  │  │  │  ├─ events_block_delete.d.ts
│  │  │  │  ├─ events_block_drag.d.ts
│  │  │  │  ├─ events_block_field_intermediate_change.d.ts
│  │  │  │  ├─ events_block_move.d.ts
│  │  │  │  ├─ events_bubble_open.d.ts
│  │  │  │  ├─ events_click.d.ts
│  │  │  │  ├─ events_comment_base.d.ts
│  │  │  │  ├─ events_comment_change.d.ts
│  │  │  │  ├─ events_comment_collapse.d.ts
│  │  │  │  ├─ events_comment_create.d.ts
│  │  │  │  ├─ events_comment_delete.d.ts
│  │  │  │  ├─ events_comment_drag.d.ts
│  │  │  │  ├─ events_comment_move.d.ts
│  │  │  │  ├─ events_comment_resize.d.ts
│  │  │  │  ├─ events_selected.d.ts
│  │  │  │  ├─ events_theme_change.d.ts
│  │  │  │  ├─ events_toolbox_item_select.d.ts
│  │  │  │  ├─ events_trashcan_open.d.ts
│  │  │  │  ├─ events_ui_base.d.ts
│  │  │  │  ├─ events_var_base.d.ts
│  │  │  │  ├─ events_var_create.d.ts
│  │  │  │  ├─ events_var_delete.d.ts
│  │  │  │  ├─ events_var_rename.d.ts
│  │  │  │  ├─ events_var_type_change.d.ts
│  │  │  │  ├─ events_viewport.d.ts
│  │  │  │  ├─ predicates.d.ts
│  │  │  │  ├─ type.d.ts
│  │  │  │  ├─ utils.d.ts
│  │  │  │  └─ workspace_events.d.ts
│  │  │  ├─ extensions.d.ts
│  │  │  ├─ field.d.ts
│  │  │  ├─ field_checkbox.d.ts
│  │  │  ├─ field_dropdown.d.ts
│  │  │  ├─ field_image.d.ts
│  │  │  ├─ field_input.d.ts
│  │  │  ├─ field_label.d.ts
│  │  │  ├─ field_label_serializable.d.ts
│  │  │  ├─ field_number.d.ts
│  │  │  ├─ field_registry.d.ts
│  │  │  ├─ field_textinput.d.ts
│  │  │  ├─ field_variable.d.ts
│  │  │  ├─ flyout_base.d.ts
│  │  │  ├─ flyout_button.d.ts
│  │  │  ├─ flyout_horizontal.d.ts
│  │  │  ├─ flyout_item.d.ts
│  │  │  ├─ flyout_metrics_manager.d.ts
│  │  │  ├─ flyout_navigator.d.ts
│  │  │  ├─ flyout_separator.d.ts
│  │  │  ├─ flyout_vertical.d.ts
│  │  │  ├─ focus_manager.d.ts
│  │  │  ├─ generator.d.ts
│  │  │  ├─ gesture.d.ts
│  │  │  ├─ grid.d.ts
│  │  │  ├─ icons
│  │  │  │  ├─ comment_icon.d.ts
│  │  │  │  ├─ exceptions.d.ts
│  │  │  │  ├─ icon.d.ts
│  │  │  │  ├─ icon_types.d.ts
│  │  │  │  ├─ mutator_icon.d.ts
│  │  │  │  ├─ registry.d.ts
│  │  │  │  └─ warning_icon.d.ts
│  │  │  ├─ icons.d.ts
│  │  │  ├─ inject.d.ts
│  │  │  ├─ inputs
│  │  │  │  ├─ align.d.ts
│  │  │  │  ├─ dummy_input.d.ts
│  │  │  │  ├─ end_row_input.d.ts
│  │  │  │  ├─ input.d.ts
│  │  │  │  ├─ input_types.d.ts
│  │  │  │  ├─ statement_input.d.ts
│  │  │  │  └─ value_input.d.ts
│  │  │  ├─ inputs.d.ts
│  │  │  ├─ insertion_marker_previewer.d.ts
│  │  │  ├─ interfaces
│  │  │  │  ├─ i_autohideable.d.ts
│  │  │  │  ├─ i_bounded_element.d.ts
│  │  │  │  ├─ i_bubble.d.ts
│  │  │  │  ├─ i_collapsible_toolbox_item.d.ts
│  │  │  │  ├─ i_comment_icon.d.ts
│  │  │  │  ├─ i_component.d.ts
│  │  │  │  ├─ i_connection_checker.d.ts
│  │  │  │  ├─ i_connection_previewer.d.ts
│  │  │  │  ├─ i_contextmenu.d.ts
│  │  │  │  ├─ i_copyable.d.ts
│  │  │  │  ├─ i_deletable.d.ts
│  │  │  │  ├─ i_delete_area.d.ts
│  │  │  │  ├─ i_draggable.d.ts
│  │  │  │  ├─ i_dragger.d.ts
│  │  │  │  ├─ i_drag_target.d.ts
│  │  │  │  ├─ i_flyout.d.ts
│  │  │  │  ├─ i_flyout_inflater.d.ts
│  │  │  │  ├─ i_focusable_node.d.ts
│  │  │  │  ├─ i_focusable_tree.d.ts
│  │  │  │  ├─ i_has_bubble.d.ts
│  │  │  │  ├─ i_icon.d.ts
│  │  │  │  ├─ i_keyboard_accessible.d.ts
│  │  │  │  ├─ i_legacy_procedure_blocks.d.ts
│  │  │  │  ├─ i_metrics_manager.d.ts
│  │  │  │  ├─ i_movable.d.ts
│  │  │  │  ├─ i_navigation_policy.d.ts
│  │  │  │  ├─ i_observable.d.ts
│  │  │  │  ├─ i_parameter_model.d.ts
│  │  │  │  ├─ i_paster.d.ts
│  │  │  │  ├─ i_positionable.d.ts
│  │  │  │  ├─ i_procedure_block.d.ts
│  │  │  │  ├─ i_procedure_map.d.ts
│  │  │  │  ├─ i_procedure_model.d.ts
│  │  │  │  ├─ i_registrable.d.ts
│  │  │  │  ├─ i_rendered_element.d.ts
│  │  │  │  ├─ i_selectable.d.ts
│  │  │  │  ├─ i_selectable_toolbox_item.d.ts
│  │  │  │  ├─ i_serializable.d.ts
│  │  │  │  ├─ i_serializer.d.ts
│  │  │  │  ├─ i_styleable.d.ts
│  │  │  │  ├─ i_toolbox.d.ts
│  │  │  │  ├─ i_toolbox_item.d.ts
│  │  │  │  ├─ i_variable_backed_parameter_model.d.ts
│  │  │  │  ├─ i_variable_map.d.ts
│  │  │  │  └─ i_variable_model.d.ts
│  │  │  ├─ internal_constants.d.ts
│  │  │  ├─ keyboard_nav
│  │  │  │  ├─ block_comment_navigation_policy.d.ts
│  │  │  │  ├─ block_navigation_policy.d.ts
│  │  │  │  ├─ comment_bar_button_navigation_policy.d.ts
│  │  │  │  ├─ comment_editor_navigation_policy.d.ts
│  │  │  │  ├─ connection_navigation_policy.d.ts
│  │  │  │  ├─ field_navigation_policy.d.ts
│  │  │  │  ├─ flyout_button_navigation_policy.d.ts
│  │  │  │  ├─ flyout_navigation_policy.d.ts
│  │  │  │  ├─ flyout_separator_navigation_policy.d.ts
│  │  │  │  ├─ icon_navigation_policy.d.ts
│  │  │  │  ├─ line_cursor.d.ts
│  │  │  │  ├─ marker.d.ts
│  │  │  │  ├─ workspace_comment_navigation_policy.d.ts
│  │  │  │  └─ workspace_navigation_policy.d.ts
│  │  │  ├─ keyboard_navigation_controller.d.ts
│  │  │  ├─ label_flyout_inflater.d.ts
│  │  │  ├─ layers.d.ts
│  │  │  ├─ layer_manager.d.ts
│  │  │  ├─ main.d.ts
│  │  │  ├─ marker_manager.d.ts
│  │  │  ├─ menu.d.ts
│  │  │  ├─ menuitem.d.ts
│  │  │  ├─ menu_separator.d.ts
│  │  │  ├─ metrics_manager.d.ts
│  │  │  ├─ msg.d.ts
│  │  │  ├─ names.d.ts
│  │  │  ├─ navigator.d.ts
│  │  │  ├─ observable_procedure_map.d.ts
│  │  │  ├─ options.d.ts
│  │  │  ├─ positionable_helpers.d.ts
│  │  │  ├─ procedures.d.ts
│  │  │  ├─ registry.d.ts
│  │  │  ├─ rendered_connection.d.ts
│  │  │  ├─ renderers
│  │  │  │  ├─ common
│  │  │  │  │  ├─ block_rendering.d.ts
│  │  │  │  │  ├─ constants.d.ts
│  │  │  │  │  ├─ drawer.d.ts
│  │  │  │  │  ├─ info.d.ts
│  │  │  │  │  ├─ i_path_object.d.ts
│  │  │  │  │  ├─ path_object.d.ts
│  │  │  │  │  └─ renderer.d.ts
│  │  │  │  ├─ geras
│  │  │  │  │  ├─ constants.d.ts
│  │  │  │  │  ├─ drawer.d.ts
│  │  │  │  │  ├─ geras.d.ts
│  │  │  │  │  ├─ highlighter.d.ts
│  │  │  │  │  ├─ highlight_constants.d.ts
│  │  │  │  │  ├─ info.d.ts
│  │  │  │  │  ├─ measurables
│  │  │  │  │  │  ├─ inline_input.d.ts
│  │  │  │  │  │  └─ statement_input.d.ts
│  │  │  │  │  ├─ path_object.d.ts
│  │  │  │  │  └─ renderer.d.ts
│  │  │  │  ├─ measurables
│  │  │  │  │  ├─ base.d.ts
│  │  │  │  │  ├─ bottom_row.d.ts
│  │  │  │  │  ├─ connection.d.ts
│  │  │  │  │  ├─ external_value_input.d.ts
│  │  │  │  │  ├─ field.d.ts
│  │  │  │  │  ├─ hat.d.ts
│  │  │  │  │  ├─ icon.d.ts
│  │  │  │  │  ├─ inline_input.d.ts
│  │  │  │  │  ├─ input_connection.d.ts
│  │  │  │  │  ├─ input_row.d.ts
│  │  │  │  │  ├─ in_row_spacer.d.ts
│  │  │  │  │  ├─ jagged_edge.d.ts
│  │  │  │  │  ├─ next_connection.d.ts
│  │  │  │  │  ├─ output_connection.d.ts
│  │  │  │  │  ├─ previous_connection.d.ts
│  │  │  │  │  ├─ round_corner.d.ts
│  │  │  │  │  ├─ row.d.ts
│  │  │  │  │  ├─ spacer_row.d.ts
│  │  │  │  │  ├─ square_corner.d.ts
│  │  │  │  │  ├─ statement_input.d.ts
│  │  │  │  │  ├─ top_row.d.ts
│  │  │  │  │  └─ types.d.ts
│  │  │  │  ├─ thrasos
│  │  │  │  │  ├─ info.d.ts
│  │  │  │  │  ├─ renderer.d.ts
│  │  │  │  │  └─ thrasos.d.ts
│  │  │  │  └─ zelos
│  │  │  │     ├─ constants.d.ts
│  │  │  │     ├─ drawer.d.ts
│  │  │  │     ├─ info.d.ts
│  │  │  │     ├─ measurables
│  │  │  │     │  ├─ bottom_row.d.ts
│  │  │  │     │  ├─ inputs.d.ts
│  │  │  │     │  ├─ row_elements.d.ts
│  │  │  │     │  └─ top_row.d.ts
│  │  │  │     ├─ path_object.d.ts
│  │  │  │     ├─ renderer.d.ts
│  │  │  │     └─ zelos.d.ts
│  │  │  ├─ render_management.d.ts
│  │  │  ├─ scrollbar.d.ts
│  │  │  ├─ scrollbar_pair.d.ts
│  │  │  ├─ separator_flyout_inflater.d.ts
│  │  │  ├─ serialization
│  │  │  │  ├─ blocks.d.ts
│  │  │  │  ├─ exceptions.d.ts
│  │  │  │  ├─ priorities.d.ts
│  │  │  │  ├─ procedures.d.ts
│  │  │  │  ├─ registry.d.ts
│  │  │  │  ├─ variables.d.ts
│  │  │  │  ├─ workspaces.d.ts
│  │  │  │  └─ workspace_comments.d.ts
│  │  │  ├─ serialization.d.ts
│  │  │  ├─ shortcut_items.d.ts
│  │  │  ├─ shortcut_registry.d.ts
│  │  │  ├─ sprites.d.ts
│  │  │  ├─ theme
│  │  │  │  ├─ classic.d.ts
│  │  │  │  ├─ themes.d.ts
│  │  │  │  └─ zelos.d.ts
│  │  │  ├─ theme.d.ts
│  │  │  ├─ theme_manager.d.ts
│  │  │  ├─ toast.d.ts
│  │  │  ├─ toolbox
│  │  │  │  ├─ category.d.ts
│  │  │  │  ├─ collapsible_category.d.ts
│  │  │  │  ├─ separator.d.ts
│  │  │  │  ├─ toolbox.d.ts
│  │  │  │  └─ toolbox_item.d.ts
│  │  │  ├─ tooltip.d.ts
│  │  │  ├─ touch.d.ts
│  │  │  ├─ trashcan.d.ts
│  │  │  ├─ utils
│  │  │  │  ├─ aria.d.ts
│  │  │  │  ├─ array.d.ts
│  │  │  │  ├─ colour.d.ts
│  │  │  │  ├─ coordinate.d.ts
│  │  │  │  ├─ deprecation.d.ts
│  │  │  │  ├─ dom.d.ts
│  │  │  │  ├─ drag.d.ts
│  │  │  │  ├─ focusable_tree_traverser.d.ts
│  │  │  │  ├─ idgenerator.d.ts
│  │  │  │  ├─ keycodes.d.ts
│  │  │  │  ├─ math.d.ts
│  │  │  │  ├─ metrics.d.ts
│  │  │  │  ├─ object.d.ts
│  │  │  │  ├─ parsing.d.ts
│  │  │  │  ├─ rect.d.ts
│  │  │  │  ├─ size.d.ts
│  │  │  │  ├─ string.d.ts
│  │  │  │  ├─ style.d.ts
│  │  │  │  ├─ svg.d.ts
│  │  │  │  ├─ svg_math.d.ts
│  │  │  │  ├─ svg_paths.d.ts
│  │  │  │  ├─ toolbox.d.ts
│  │  │  │  ├─ useragent.d.ts
│  │  │  │  └─ xml.d.ts
│  │  │  ├─ utils.d.ts
│  │  │  ├─ variables.d.ts
│  │  │  ├─ variables_dynamic.d.ts
│  │  │  ├─ variable_map.d.ts
│  │  │  ├─ variable_model.d.ts
│  │  │  ├─ widgetdiv.d.ts
│  │  │  ├─ workspace.d.ts
│  │  │  ├─ workspace_audio.d.ts
│  │  │  ├─ workspace_dragger.d.ts
│  │  │  ├─ workspace_svg.d.ts
│  │  │  ├─ xml.d.ts
│  │  │  └─ zoom_controls.d.ts
│  │  ├─ core-node.js
│  │  ├─ core.d.ts
│  │  ├─ core.js
│  │  ├─ dart.d.ts
│  │  ├─ dart.js
│  │  ├─ dart.mjs
│  │  ├─ dart_compressed.js
│  │  ├─ dart_compressed.js.map
│  │  ├─ generators
│  │  │  ├─ dart
│  │  │  │  ├─ dart_generator.d.ts
│  │  │  │  ├─ lists.d.ts
│  │  │  │  ├─ logic.d.ts
│  │  │  │  ├─ loops.d.ts
│  │  │  │  ├─ math.d.ts
│  │  │  │  ├─ procedures.d.ts
│  │  │  │  ├─ text.d.ts
│  │  │  │  ├─ variables.d.ts
│  │  │  │  └─ variables_dynamic.d.ts
│  │  │  ├─ dart.d.ts
│  │  │  ├─ javascript
│  │  │  │  ├─ javascript_generator.d.ts
│  │  │  │  ├─ lists.d.ts
│  │  │  │  ├─ logic.d.ts
│  │  │  │  ├─ loops.d.ts
│  │  │  │  ├─ math.d.ts
│  │  │  │  ├─ procedures.d.ts
│  │  │  │  ├─ text.d.ts
│  │  │  │  ├─ variables.d.ts
│  │  │  │  └─ variables_dynamic.d.ts
│  │  │  ├─ javascript.d.ts
│  │  │  ├─ lua
│  │  │  │  ├─ lists.d.ts
│  │  │  │  ├─ logic.d.ts
│  │  │  │  ├─ loops.d.ts
│  │  │  │  ├─ lua_generator.d.ts
│  │  │  │  ├─ math.d.ts
│  │  │  │  ├─ procedures.d.ts
│  │  │  │  ├─ text.d.ts
│  │  │  │  ├─ variables.d.ts
│  │  │  │  └─ variables_dynamic.d.ts
│  │  │  ├─ lua.d.ts
│  │  │  ├─ php
│  │  │  │  ├─ lists.d.ts
│  │  │  │  ├─ logic.d.ts
│  │  │  │  ├─ loops.d.ts
│  │  │  │  ├─ math.d.ts
│  │  │  │  ├─ php_generator.d.ts
│  │  │  │  ├─ procedures.d.ts
│  │  │  │  ├─ text.d.ts
│  │  │  │  ├─ variables.d.ts
│  │  │  │  └─ variables_dynamic.d.ts
│  │  │  ├─ php.d.ts
│  │  │  ├─ python
│  │  │  │  ├─ lists.d.ts
│  │  │  │  ├─ logic.d.ts
│  │  │  │  ├─ loops.d.ts
│  │  │  │  ├─ math.d.ts
│  │  │  │  ├─ procedures.d.ts
│  │  │  │  ├─ python_generator.d.ts
│  │  │  │  ├─ text.d.ts
│  │  │  │  ├─ variables.d.ts
│  │  │  │  └─ variables_dynamic.d.ts
│  │  │  └─ python.d.ts
│  │  ├─ index.d.ts
│  │  ├─ index.js
│  │  ├─ index.mjs
│  │  ├─ javascript.d.ts
│  │  ├─ javascript.js
│  │  ├─ javascript.mjs
│  │  ├─ javascript_compressed.js
│  │  ├─ javascript_compressed.js.map
│  │  ├─ lua.d.ts
│  │  ├─ lua.js
│  │  ├─ lua.mjs
│  │  ├─ lua_compressed.js
│  │  ├─ lua_compressed.js.map
│  │  ├─ media
│  │  │  ├─ 1x1.gif
│  │  │  ├─ click.mp3
│  │  │  ├─ click.ogg
│  │  │  ├─ click.wav
│  │  │  ├─ delete-icon.svg
│  │  │  ├─ delete.mp3
│  │  │  ├─ delete.ogg
│  │  │  ├─ delete.wav
│  │  │  ├─ disconnect.mp3
│  │  │  ├─ disconnect.ogg
│  │  │  ├─ disconnect.wav
│  │  │  ├─ dropdown-arrow.svg
│  │  │  ├─ foldout-icon.svg
│  │  │  ├─ handclosed.cur
│  │  │  ├─ handdelete.cur
│  │  │  ├─ handopen.cur
│  │  │  ├─ pilcrow.png
│  │  │  ├─ quote0.png
│  │  │  ├─ quote1.png
│  │  │  ├─ resize-handle.svg
│  │  │  ├─ sprites.png
│  │  │  └─ sprites.svg
│  │  ├─ msg
│  │  │  ├─ ab.d.ts
│  │  │  ├─ ab.js
│  │  │  ├─ ab.mjs
│  │  │  ├─ ace.d.ts
│  │  │  ├─ ace.js
│  │  │  ├─ ace.mjs
│  │  │  ├─ af.d.ts
│  │  │  ├─ af.js
│  │  │  ├─ af.mjs
│  │  │  ├─ am.d.ts
│  │  │  ├─ am.js
│  │  │  ├─ am.mjs
│  │  │  ├─ ar.d.ts
│  │  │  ├─ ar.js
│  │  │  ├─ ar.mjs
│  │  │  ├─ ast.d.ts
│  │  │  ├─ ast.js
│  │  │  ├─ ast.mjs
│  │  │  ├─ az.d.ts
│  │  │  ├─ az.js
│  │  │  ├─ az.mjs
│  │  │  ├─ ba.d.ts
│  │  │  ├─ ba.js
│  │  │  ├─ ba.mjs
│  │  │  ├─ bcc.d.ts
│  │  │  ├─ bcc.js
│  │  │  ├─ bcc.mjs
│  │  │  ├─ be-tarask.d.ts
│  │  │  ├─ be-tarask.js
│  │  │  ├─ be-tarask.mjs
│  │  │  ├─ be.d.ts
│  │  │  ├─ be.js
│  │  │  ├─ be.mjs
│  │  │  ├─ bg.d.ts
│  │  │  ├─ bg.js
│  │  │  ├─ bg.mjs
│  │  │  ├─ bn.d.ts
│  │  │  ├─ bn.js
│  │  │  ├─ bn.mjs
│  │  │  ├─ br.d.ts
│  │  │  ├─ br.js
│  │  │  ├─ br.mjs
│  │  │  ├─ bs.d.ts
│  │  │  ├─ bs.js
│  │  │  ├─ bs.mjs
│  │  │  ├─ ca.d.ts
│  │  │  ├─ ca.js
│  │  │  ├─ ca.mjs
│  │  │  ├─ cdo.d.ts
│  │  │  ├─ cdo.js
│  │  │  ├─ cdo.mjs
│  │  │  ├─ ce.d.ts
│  │  │  ├─ ce.js
│  │  │  ├─ ce.mjs
│  │  │  ├─ cs.d.ts
│  │  │  ├─ cs.js
│  │  │  ├─ cs.mjs
│  │  │  ├─ da.d.ts
│  │  │  ├─ da.js
│  │  │  ├─ da.mjs
│  │  │  ├─ de.d.ts
│  │  │  ├─ de.js
│  │  │  ├─ de.mjs
│  │  │  ├─ diq.d.ts
│  │  │  ├─ diq.js
│  │  │  ├─ diq.mjs
│  │  │  ├─ dtp.d.ts
│  │  │  ├─ dtp.js
│  │  │  ├─ dtp.mjs
│  │  │  ├─ dty.d.ts
│  │  │  ├─ dty.js
│  │  │  ├─ dty.mjs
│  │  │  ├─ ee.d.ts
│  │  │  ├─ ee.js
│  │  │  ├─ ee.mjs
│  │  │  ├─ el.d.ts
│  │  │  ├─ el.js
│  │  │  ├─ el.mjs
│  │  │  ├─ en-gb.d.ts
│  │  │  ├─ en-gb.js
│  │  │  ├─ en-gb.mjs
│  │  │  ├─ en.d.ts
│  │  │  ├─ en.js
│  │  │  ├─ en.mjs
│  │  │  ├─ eo.d.ts
│  │  │  ├─ eo.js
│  │  │  ├─ eo.mjs
│  │  │  ├─ es.d.ts
│  │  │  ├─ es.js
│  │  │  ├─ es.mjs
│  │  │  ├─ et.d.ts
│  │  │  ├─ et.js
│  │  │  ├─ et.mjs
│  │  │  ├─ eu.d.ts
│  │  │  ├─ eu.js
│  │  │  ├─ eu.mjs
│  │  │  ├─ fa.d.ts
│  │  │  ├─ fa.js
│  │  │  ├─ fa.mjs
│  │  │  ├─ fi.d.ts
│  │  │  ├─ fi.js
│  │  │  ├─ fi.mjs
│  │  │  ├─ fo.d.ts
│  │  │  ├─ fo.js
│  │  │  ├─ fo.mjs
│  │  │  ├─ fr.d.ts
│  │  │  ├─ fr.js
│  │  │  ├─ fr.mjs
│  │  │  ├─ frr.d.ts
│  │  │  ├─ frr.js
│  │  │  ├─ frr.mjs
│  │  │  ├─ gl.d.ts
│  │  │  ├─ gl.js
│  │  │  ├─ gl.mjs
│  │  │  ├─ gn.d.ts
│  │  │  ├─ gn.js
│  │  │  ├─ gn.mjs
│  │  │  ├─ gor.d.ts
│  │  │  ├─ gor.js
│  │  │  ├─ gor.mjs
│  │  │  ├─ ha.d.ts
│  │  │  ├─ ha.js
│  │  │  ├─ ha.mjs
│  │  │  ├─ hak.d.ts
│  │  │  ├─ hak.js
│  │  │  ├─ hak.mjs
│  │  │  ├─ he.d.ts
│  │  │  ├─ he.js
│  │  │  ├─ he.mjs
│  │  │  ├─ hi.d.ts
│  │  │  ├─ hi.js
│  │  │  ├─ hi.mjs
│  │  │  ├─ hr.d.ts
│  │  │  ├─ hr.js
│  │  │  ├─ hr.mjs
│  │  │  ├─ hrx.d.ts
│  │  │  ├─ hrx.js
│  │  │  ├─ hrx.mjs
│  │  │  ├─ hsb.d.ts
│  │  │  ├─ hsb.js
│  │  │  ├─ hsb.mjs
│  │  │  ├─ hu.d.ts
│  │  │  ├─ hu.js
│  │  │  ├─ hu.mjs
│  │  │  ├─ hy.d.ts
│  │  │  ├─ hy.js
│  │  │  ├─ hy.mjs
│  │  │  ├─ ia.d.ts
│  │  │  ├─ ia.js
│  │  │  ├─ ia.mjs
│  │  │  ├─ id.d.ts
│  │  │  ├─ id.js
│  │  │  ├─ id.mjs
│  │  │  ├─ ig.d.ts
│  │  │  ├─ ig.js
│  │  │  ├─ ig.mjs
│  │  │  ├─ inh.d.ts
│  │  │  ├─ inh.js
│  │  │  ├─ inh.mjs
│  │  │  ├─ is.d.ts
│  │  │  ├─ is.js
│  │  │  ├─ is.mjs
│  │  │  ├─ it.d.ts
│  │  │  ├─ it.js
│  │  │  ├─ it.mjs
│  │  │  ├─ ja.d.ts
│  │  │  ├─ ja.js
│  │  │  ├─ ja.mjs
│  │  │  ├─ ka.d.ts
│  │  │  ├─ ka.js
│  │  │  ├─ ka.mjs
│  │  │  ├─ kab.d.ts
│  │  │  ├─ kab.js
│  │  │  ├─ kab.mjs
│  │  │  ├─ kbd-cyrl.d.ts
│  │  │  ├─ kbd-cyrl.js
│  │  │  ├─ kbd-cyrl.mjs
│  │  │  ├─ km.d.ts
│  │  │  ├─ km.js
│  │  │  ├─ km.mjs
│  │  │  ├─ kn.d.ts
│  │  │  ├─ kn.js
│  │  │  ├─ kn.mjs
│  │  │  ├─ ko.d.ts
│  │  │  ├─ ko.js
│  │  │  ├─ ko.mjs
│  │  │  ├─ ksh.d.ts
│  │  │  ├─ ksh.js
│  │  │  ├─ ksh.mjs
│  │  │  ├─ ku-latn.d.ts
│  │  │  ├─ ku-latn.js
│  │  │  ├─ ku-latn.mjs
│  │  │  ├─ ky.d.ts
│  │  │  ├─ ky.js
│  │  │  ├─ ky.mjs
│  │  │  ├─ la.d.ts
│  │  │  ├─ la.js
│  │  │  ├─ la.mjs
│  │  │  ├─ lb.d.ts
│  │  │  ├─ lb.js
│  │  │  ├─ lb.mjs
│  │  │  ├─ lki.d.ts
│  │  │  ├─ lki.js
│  │  │  ├─ lki.mjs
│  │  │  ├─ lo.d.ts
│  │  │  ├─ lo.js
│  │  │  ├─ lo.mjs
│  │  │  ├─ lrc.d.ts
│  │  │  ├─ lrc.js
│  │  │  ├─ lrc.mjs
│  │  │  ├─ lt.d.ts
│  │  │  ├─ lt.js
│  │  │  ├─ lt.mjs
│  │  │  ├─ lv.d.ts
│  │  │  ├─ lv.js
│  │  │  ├─ lv.mjs
│  │  │  ├─ mg.d.ts
│  │  │  ├─ mg.js
│  │  │  ├─ mg.mjs
│  │  │  ├─ mk.d.ts
│  │  │  ├─ mk.js
│  │  │  ├─ mk.mjs
│  │  │  ├─ ml.d.ts
│  │  │  ├─ ml.js
│  │  │  ├─ ml.mjs
│  │  │  ├─ mnw.d.ts
│  │  │  ├─ mnw.js
│  │  │  ├─ mnw.mjs
│  │  │  ├─ ms.d.ts
│  │  │  ├─ ms.js
│  │  │  ├─ ms.mjs
│  │  │  ├─ msg.d.ts
│  │  │  ├─ my.d.ts
│  │  │  ├─ my.js
│  │  │  ├─ my.mjs
│  │  │  ├─ mzn.d.ts
│  │  │  ├─ mzn.js
│  │  │  ├─ mzn.mjs
│  │  │  ├─ nb.d.ts
│  │  │  ├─ nb.js
│  │  │  ├─ nb.mjs
│  │  │  ├─ ne.d.ts
│  │  │  ├─ ne.js
│  │  │  ├─ ne.mjs
│  │  │  ├─ nl.d.ts
│  │  │  ├─ nl.js
│  │  │  ├─ nl.mjs
│  │  │  ├─ oc.d.ts
│  │  │  ├─ oc.js
│  │  │  ├─ oc.mjs
│  │  │  ├─ olo.d.ts
│  │  │  ├─ olo.js
│  │  │  ├─ olo.mjs
│  │  │  ├─ pa.d.ts
│  │  │  ├─ pa.js
│  │  │  ├─ pa.mjs
│  │  │  ├─ pl.d.ts
│  │  │  ├─ pl.js
│  │  │  ├─ pl.mjs
│  │  │  ├─ pms.d.ts
│  │  │  ├─ pms.js
│  │  │  ├─ pms.mjs
│  │  │  ├─ ps.d.ts
│  │  │  ├─ ps.js
│  │  │  ├─ ps.mjs
│  │  │  ├─ pt-br.d.ts
│  │  │  ├─ pt-br.js
│  │  │  ├─ pt-br.mjs
│  │  │  ├─ pt.d.ts
│  │  │  ├─ pt.js
│  │  │  ├─ pt.mjs
│  │  │  ├─ ro.d.ts
│  │  │  ├─ ro.js
│  │  │  ├─ ro.mjs
│  │  │  ├─ ru.d.ts
│  │  │  ├─ ru.js
│  │  │  ├─ ru.mjs
│  │  │  ├─ sc.d.ts
│  │  │  ├─ sc.js
│  │  │  ├─ sc.mjs
│  │  │  ├─ sco.d.ts
│  │  │  ├─ sco.js
│  │  │  ├─ sco.mjs
│  │  │  ├─ sd.d.ts
│  │  │  ├─ sd.js
│  │  │  ├─ sd.mjs
│  │  │  ├─ shn.d.ts
│  │  │  ├─ shn.js
│  │  │  ├─ shn.mjs
│  │  │  ├─ si.d.ts
│  │  │  ├─ si.js
│  │  │  ├─ si.mjs
│  │  │  ├─ sk.d.ts
│  │  │  ├─ sk.js
│  │  │  ├─ sk.mjs
│  │  │  ├─ skr-arab.d.ts
│  │  │  ├─ skr-arab.js
│  │  │  ├─ skr-arab.mjs
│  │  │  ├─ sl.d.ts
│  │  │  ├─ sl.js
│  │  │  ├─ sl.mjs
│  │  │  ├─ smn.d.ts
│  │  │  ├─ smn.js
│  │  │  ├─ smn.mjs
│  │  │  ├─ sq.d.ts
│  │  │  ├─ sq.js
│  │  │  ├─ sq.mjs
│  │  │  ├─ sr-latn.d.ts
│  │  │  ├─ sr-latn.js
│  │  │  ├─ sr-latn.mjs
│  │  │  ├─ sr.d.ts
│  │  │  ├─ sr.js
│  │  │  ├─ sr.mjs
│  │  │  ├─ sv.d.ts
│  │  │  ├─ sv.js
│  │  │  ├─ sv.mjs
│  │  │  ├─ sw.d.ts
│  │  │  ├─ sw.js
│  │  │  ├─ sw.mjs
│  │  │  ├─ ta.d.ts
│  │  │  ├─ ta.js
│  │  │  ├─ ta.mjs
│  │  │  ├─ tcy.d.ts
│  │  │  ├─ tcy.js
│  │  │  ├─ tcy.mjs
│  │  │  ├─ tdd.d.ts
│  │  │  ├─ tdd.js
│  │  │  ├─ tdd.mjs
│  │  │  ├─ te.d.ts
│  │  │  ├─ te.js
│  │  │  ├─ te.mjs
│  │  │  ├─ th.d.ts
│  │  │  ├─ th.js
│  │  │  ├─ th.mjs
│  │  │  ├─ ti.d.ts
│  │  │  ├─ ti.js
│  │  │  ├─ ti.mjs
│  │  │  ├─ tl.d.ts
│  │  │  ├─ tl.js
│  │  │  ├─ tl.mjs
│  │  │  ├─ tlh.d.ts
│  │  │  ├─ tlh.js
│  │  │  ├─ tlh.mjs
│  │  │  ├─ tr.d.ts
│  │  │  ├─ tr.js
│  │  │  ├─ tr.mjs
│  │  │  ├─ ug-arab.d.ts
│  │  │  ├─ ug-arab.js
│  │  │  ├─ ug-arab.mjs
│  │  │  ├─ uk.d.ts
│  │  │  ├─ uk.js
│  │  │  ├─ uk.mjs
│  │  │  ├─ ur.d.ts
│  │  │  ├─ ur.js
│  │  │  ├─ ur.mjs
│  │  │  ├─ uz.d.ts
│  │  │  ├─ uz.js
│  │  │  ├─ uz.mjs
│  │  │  ├─ vi.d.ts
│  │  │  ├─ vi.js
│  │  │  ├─ vi.mjs
│  │  │  ├─ xmf.d.ts
│  │  │  ├─ xmf.js
│  │  │  ├─ xmf.mjs
│  │  │  ├─ yo.d.ts
│  │  │  ├─ yo.js
│  │  │  ├─ yo.mjs
│  │  │  ├─ zgh.d.ts
│  │  │  ├─ zgh.js
│  │  │  ├─ zgh.mjs
│  │  │  ├─ zh-hans.d.ts
│  │  │  ├─ zh-hans.js
│  │  │  ├─ zh-hans.mjs
│  │  │  ├─ zh-hant.d.ts
│  │  │  ├─ zh-hant.js
│  │  │  └─ zh-hant.mjs
│  │  ├─ package.json
│  │  ├─ php.d.ts
│  │  ├─ php.js
│  │  ├─ php.mjs
│  │  ├─ php_compressed.js
│  │  ├─ php_compressed.js.map
│  │  ├─ python.d.ts
│  │  ├─ python.js
│  │  ├─ python.mjs
│  │  ├─ python_compressed.js
│  │  ├─ python_compressed.js.map
│  │  └─ README.md
│  ├─ index.html
│  ├─ index.py
│  └─ script
│     ├─ index.js
│     ├─ logo_only.svg
│     └─ python_custom.js
├─ cleanup.py
├─ CMakeLists.txt
├─ py_exe
│  └─ icon.ico
├─ README.md
└─ vscode_ext
   ├─ CHANGELOG.md
   ├─ eslint.config.mjs
   ├─ extension.js
   ├─ icon.ico
   ├─ icon.png
   ├─ jsconfig.json
   ├─ LICENSE.md
   ├─ package-lock.json
   ├─ package.json
   └─ README.md

```
