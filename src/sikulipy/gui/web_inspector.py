import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, 
    QListWidget, QLabel, QGraphicsView, QGraphicsScene, 
    QGraphicsRectItem, QListWidgetItem, QRadioButton, QButtonGroup, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QRectF
from PyQt6.QtGui import QPixmap, QColor, QPen, QImage, QPainter

class WebInspectorWorker(QThread):
    finished_capture = pyqtSignal(object, list) # pixmap, elements
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(viewport={'width': 1920, 'height': 1080})
                page = context.new_page()
                page.goto(self.url, wait_until='load', timeout=60000)
                # Wait a brief moment for dynamic JS to render elements
                page.wait_for_timeout(3000)
                
                # Take screenshot
                screenshot_bytes = page.screenshot(full_page=True)
                
                # Evaluate JS to get bounding boxes
                js_script = """
                () => {
                    function getBounds(selector, category) {
                        const els = document.querySelectorAll(selector);
                        let results = [];
                        els.forEach((el, index) => {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {
                                const ariaLabel = el.getAttribute('aria-label') || '';
                                const altText = el.alt || el.title || '';
                                const srcText = el.src ? new URL(el.src, window.location.href).pathname.split('/').pop() : '';
                                const label = (el.innerText || el.value || el.placeholder || altText || srcText || '').substring(0, 30).trim();
                                results.push({
                                    id: category + '_' + index,
                                    category: category,
                                    text: label,
                                    ariaLabel: ariaLabel.substring(0, 30).trim(),
                                    x: rect.x + window.scrollX,
                                    y: rect.y + window.scrollY,
                                    w: rect.width,
                                    h: rect.height
                                });
                            }
                        });
                        return results;
                    }
                    
                    let all_els = [];
                    all_els.push(...getBounds('a', 'Links'));
                    all_els.push(...getBounds('button, input[type="button"], input[type="submit"]', 'Buttons'));
                    all_els.push(...getBounds('input:not([type="button"]):not([type="submit"]):not([type="checkbox"]):not([type="radio"]), textarea', 'Inputs'));
                    all_els.push(...getBounds('input[type="checkbox"], input[type="radio"]', 'Checkbox & Radio'));
                    all_els.push(...getBounds('select', 'Selects & Dropdowns'));
                    all_els.push(...getBounds('[role="menuitem"], .menu-item', 'Menu Items'));
                    all_els.push(...getBounds('img', 'Images'));
                    
                    return all_els;
                }
                """
                elements = page.evaluate(js_script)
                browser.close()
                
                image = QImage.fromData(screenshot_bytes)
                pixmap = QPixmap.fromImage(image)
                
                self.finished_capture.emit(pixmap, elements)
        except Exception as e:
            self.error.emit(str(e))

class SelectableRectItem(QGraphicsRectItem):
    def __init__(self, element_data, callback, parent=None):
        super().__init__(parent)
        self.element_data = element_data
        self.callback = callback
        
        x, y, w, h = element_data['x'], element_data['y'], element_data['w'], element_data['h']
        self.setRect(QRectF(x, y, w, h))
        
        self.setPen(QPen(QColor(255, 0, 0), 2))
        self.setBrush(QColor(255, 0, 0, 50))
        self.setAcceptHoverEvents(True)
        self.is_selected = False

    def hoverEnterEvent(self, event):
        if not self.is_selected:
            self.setPen(QPen(QColor(0, 255, 0), 3))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.is_selected:
            self.setPen(QPen(QColor(255, 0, 0), 2))
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        self.callback(self)
        super().mousePressEvent(event)
        
    def set_selected(self, selected):
        self.is_selected = selected
        if selected:
            self.setPen(QPen(QColor(0, 0, 255), 3))
            self.setBrush(QColor(0, 0, 255, 80))
        else:
            self.setPen(QPen(QColor(255, 0, 0), 2))
            self.setBrush(QColor(255, 0, 0, 50))

class WebInspectorCanvas(QGraphicsView):
    elementClicked = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        self.pixmap_item = None
        self.rect_items = []
        self.selected_rect = None
        self.full_pixmap = None

    def set_image(self, pixmap):
        self.scene.clear()
        self.rect_items.clear()
        self.selected_rect = None
        self.full_pixmap = pixmap
        
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))

    def draw_elements(self, elements, checked_ids=None):
        for r in self.rect_items:
            self.scene.removeItem(r)
        self.rect_items.clear()
        
        for el in elements:
            rect = SelectableRectItem(el, self.on_rect_clicked)
            self.scene.addItem(rect)
            self.rect_items.append(rect)
            if checked_ids is not None:
                rect.setVisible(el['id'] in checked_ids)

    def set_rect_visible(self, el_id, visible):
        for r in self.rect_items:
            if r.element_data['id'] == el_id:
                r.setVisible(visible)
                if visible:
                    self.ensureVisible(r, 50, 50)
                break

    def on_rect_clicked(self, rect_item):
        if self.selected_rect:
            self.selected_rect.set_selected(False)
        
        self.selected_rect = rect_item
        self.selected_rect.set_selected(True)
        self.elementClicked.emit(rect_item.element_data)

    def select_element_by_id(self, el_id):
        for r in self.rect_items:
            if r.element_data['id'] == el_id:
                self.on_rect_clicked(r)
                self.ensureVisible(r, 50, 50)
                break

    def get_selected_pixmap(self):
        if not self.selected_rect or not self.full_pixmap:
            return None
        rect = self.selected_rect.rect()
        return self.full_pixmap.copy(int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()))

class WebInspectorPane(QWidget):
    applyFilters = pyqtSignal(list)
    takeScreenshot = pyqtSignal()
    closeInspector = pyqtSignal()
    listItemSelected = pyqtSignal(str)
    itemCheckChanged = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.setStyleSheet("""
            QWidget { 
                background-color: #252526; 
                color: #CCCCCC; 
            }
            QCheckBox::indicator {
                border: 1px solid #CCCCCC;
                width: 14px;
                height: 14px;
                background-color: #1E1E1E;
                border-radius: 2px;
            }
            QCheckBox::indicator:checked {
                background-color: #007ACC;
                border: 1px solid #007ACC;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #007ACC;
            }
        """)
        
        self.cb_links = QCheckBox("Links")
        self.cb_buttons = QCheckBox("Buttons")
        self.cb_inputs = QCheckBox("Inputs")
        self.cb_checkbox_radio = QCheckBox("Checkbox & Radio")
        self.cb_selects = QCheckBox("Selects & Dropdowns")
        self.cb_menus = QCheckBox("Menu Items")
        self.cb_images = QCheckBox("Images")
        
        self.checkboxes = [
            (self.cb_links, "Links"),
            (self.cb_buttons, "Buttons"),
            (self.cb_inputs, "Inputs"),
            (self.cb_checkbox_radio, "Checkbox & Radio"),
            (self.cb_selects, "Selects & Dropdowns"),
            (self.cb_menus, "Menu Items"),
            (self.cb_images, "Images")
        ]
        
        for cb, _ in self.checkboxes:
            layout.addWidget(cb)
            
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._on_apply)
        
        self.take_btn = QPushButton("Take ElsScrht")
        self.take_btn.clicked.connect(self.takeScreenshot.emit)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.closeInspector.emit)
        
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.take_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)
        
        # --- Mode selection ---
        mode_frame = QFrame()
        mode_frame.setFrameShape(QFrame.Shape.StyledPanel)
        mode_frame.setStyleSheet("border: 1px solid #555; border-radius: 3px; padding: 2px;")
        mode_layout = QHBoxLayout(mode_frame)
        mode_layout.setContentsMargins(4, 2, 4, 2)
        
        self.rb_generate = QRadioButton("Generate Tests")
        self.rb_update = QRadioButton("Update Baseline")
        self.rb_generate.setChecked(True)
        
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.rb_generate, 0)
        self.mode_group.addButton(self.rb_update, 1)
        
        mode_layout.addWidget(self.rb_generate)
        mode_layout.addWidget(self.rb_update)
        layout.addWidget(mode_frame)
        
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_list_clicked)
        self.list_widget.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.list_widget)
        
        self.preview_label = QLabel("No element selected.")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #1E1E1E;")
        self.preview_label.setMinimumHeight(150)
        layout.addWidget(self.preview_label)

    def _on_apply(self):
        active_cats = [cat for cb, cat in self.checkboxes if cb.isChecked()]
        self.applyFilters.emit(active_cats)

    def _on_list_clicked(self, item):
        el_id = item.data(Qt.ItemDataRole.UserRole)
        self.listItemSelected.emit(el_id)

    def _on_item_changed(self, item):
        el_id = item.data(Qt.ItemDataRole.UserRole)
        checked = (item.checkState() == Qt.CheckState.Checked)
        self.itemCheckChanged.emit(el_id, checked)

    def update_list(self, elements):
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        
        # If > 10 elements, don't check them by default
        initial_state = Qt.CheckState.Checked if len(elements) <= 10 else Qt.CheckState.Unchecked
        
        for el in elements:
            display_text = el['text'] if el['text'] else el.get('ariaLabel', '')
            text = f"[{el['category']}] {display_text}" if display_text else f"[{el['category']}] {el['id']}"
            item = QListWidgetItem(text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            item.setCheckState(initial_state)
            item.setData(Qt.ItemDataRole.UserRole, el['id'])
            # Store the category in UserRole+1 for easy retrieval during capture
            item.setData(Qt.ItemDataRole.UserRole + 1, el['category'])
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)
            
    def select_list_item(self, el_id):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == el_id:
                self.list_widget.setCurrentItem(item)
                break
                
    def set_preview_image(self, pixmap):
        scaled = pixmap.scaled(self.preview_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(scaled)
