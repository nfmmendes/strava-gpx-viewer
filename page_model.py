from PyQt6.QtCore import QSortFilterProxyModel

class PageModel(QSortFilterProxyModel):
    def __init__(self, max_rows=50, parent=None):
        super().__init__(parent)
        self._max_rows = max(1, max_rows)
        self._current_page = -1
        # the model is empty, the row range is therefore invalid
        self.row_range = range(0)

    def setMaxRows(self, max_rows):
        model_rows_count = self.sourceModel().rowCount()

        if self._max_rows == max_rows:
            return
        if max_rows <= 0:
            return
        if max_rows >= model_rows_count:
            return

        self._max_rows = max_rows
        first_row = min(self._current_page * self._max_rows, model_rows_count)
        last_row = min((self._current_page + 1) * self._max_rows, model_rows_count)

        self.row_range = range(first_row, last_row)
        self.invalidateFilter()

    def setCurrentPage(self, page):
        if self._current_page == page:
            return

        model_rows_count = self.sourceModel().rowCount()

        if self.sourceModel() and page >= 0 and page*self._max_rows < model_rows_count:
            self._current_page = page
            
            first_row = min(self._current_page * self._max_rows, model_rows_count)
            last_row = min((self._current_page + 1) * self._max_rows, model_rows_count)

            self.row_range = range(first_row, last_row)
            self.invalidateFilter()

    def filterAcceptsRow(self, row, parent):
        return row in self.row_range

    def setSourceModel(self, model):
        old = self.sourceModel()
        if old == model:
            return

        super().setSourceModel(model)

        if not model:
            self.rowRange = range(0)
        else:
            self.setCurrentPage(0)

        self.invalidateFilter()

