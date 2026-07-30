def edit_template(self):
        item = self.tree.currentItem()
        all_queries = self.query_manager.get_all_queries()
        if not item:
            QMessageBox.warning(self, 'Select', 'Select a query first')
            return
        name = item.text(0)
        template, ok = QInputDialog.getMultiLineText(self, 'Recovery SQL template', f'Edit template for {name}:', item.text(2))
        if ok:
            for q in all_queries:
                if (q["name"] == name):
                    if not template:
                        q["recovery_template"] = "No Recovery Template"
                    else:
                        q["recovery_template"] = template
                    self.query_manager.save_queries()
            QMessageBox.information(self, 'Updated', f'Recovery template for {name} updated')