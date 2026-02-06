from PyQt6.QtCore import (QSortFilterProxyModel, 
                          Qt, 
                          QObject, 
                          QModelIndex, 
                          QAbstractItemModel)

class PageModel(QSortFilterProxyModel):
    def __init__(self, max_rows: int =50, parent: QObject =None):
        """
        Class constructor
        
        :param max_rows: Maximum number of rows to display per page.
        :type max_rows: int
        :param parent: Parent QObject.
        :type parent: QObject
        """
        super().__init__(parent)
        self._max_rows = max(1, max_rows)
        self.setDynamicSortFilter(True)
        self._current_page = -1
        # the model is empty, the row range is therefore invalid
        self.row_range = range(0)

    def sort(self, column: int, order: Qt.SortOrder):
        """
        Sort the model rows based on the given column and order.
        
        :param column: The column index to sort by.
        :type column: int
        :param order: The sort order (ascending or descending).
        :type order: Qt.SortOrder
        :return: None
        :rtype: None
        """
        reverse = (order == Qt.SortOrder.DescendingOrder)
        self.sourceModel()._data.sort_values(by = self.sourceModel()._data.columns[column], ascending= reverse, inplace=True)
        self.layoutChanged.emit()
        self.invalidateFilter()

    def setMaxRows(self, max_rows: int) -> None:
        """
        Set the max number of rows in a page.
        
        :param max_rows: The maximum number of rows to display per page.
        :type max_rows: int
        :return: None
        :rtype: None
        """
        if max_rows <= 0:
            return
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

    def setCurrentPage(self, page: int) -> None:
        """
        Set the current page to be displayed.
        
        :param page: The page index to be displayed.
        :type page: int
        :return: None
        :rtype: None
        """
        if self._current_page == page:
            return

        model_rows_count = self.sourceModel().rowCount()

        if self.sourceModel() and page >= 0 and page*self._max_rows < model_rows_count:
            self._current_page = page
            
            first_row = min(self._current_page * self._max_rows, model_rows_count)
            last_row = min((self._current_page + 1) * self._max_rows, model_rows_count)

            self.row_range = range(first_row, last_row)
            self.invalidateFilter()

    def filterAcceptsRow(self, row: int, parent: QModelIndex) -> bool:
        """
        Determine whether a given row should be accepted based on the current page's row range.
        
        :param row: The row index to check.
        :type row: int
        :param parent: The parent index (unused in this implementation).
        :type parent: QModelIndex
        :return: True if the row is within the current page's row range, False otherwise.
        """
        return row in self.row_range

    def setSourceModel(self, model: QAbstractItemModel) -> None:
        """
        Set the source model for this proxy model.
        
        :param model: The source model to be set.
        :type model: QAbstractItemModel
        :return: None
        :rtype: None
        """
        old = self.sourceModel()
        if old == model:
            return

        super().setSourceModel(model)

        if not model:
            self.rowRange = range(0)
        else:
            self.setCurrentPage(0)

        self._headers = [model.headerData(column, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)  
                         for column in range(model.columnCount())]
        self.invalidateFilter()

    def data_by_column_name(self, row: int, columnName: str) -> str:
        """
        Get the data of a given row and column name.
        
        :param row: The row index to get the data from.
        :type row: int
        :param columnName: The name of the column to get the data from.
        :type columnName: str
        :return: The data at the specified row and column, or None if the column name is not found.
        """
        column_index = self._headers.index(columnName)
    
        if column_index >= 0:
           return self.index(row, column_index).data()
       
        return None