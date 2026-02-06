from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
from pandas import DataFrame

class PandasModel(QAbstractTableModel):

    def __init__(self, data: DataFrame):
        """
        Class constructor

        :param data: The pandas DataFrame to be displayed in the model.
        :type data: pandas.DataFrame
        """
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent: QModelIndex=None) -> int:
        """
        Get the number of rows in the model.
        
        :param parent: The parent index (unused in this implementation).
        :type parent: QModelIndex
        :return: The number of rows in the model.
        :rtype: int
        """
        return self._data.shape[0]

    def columnCount(self, parent: QModelIndex=None) -> int:
        """
        Get the number of columns in the model.
        
        :param parent: The parent index (unused in this implementation).
        :type parent: QModelIndex
        :return: The number of columns in the model.
        :rtype: int
        """
        return self._data.shape[1]

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> str | None:
        """
        Get the data for a given index and role.
        
        :param index: The index of the item to retrieve data for.
        :type index: QModelIndex
        :param role: The role of the item to retrieve data for.
        :type role: Qt.ItemDataRole
        :return: The data for the given index and role, or None if not available.
        """
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])

        return None

    def headerData(self, col: int, orientation: Qt.Orientation, role: Qt.ItemDataRole) -> str | None:
        """
        Get the header data for a given column, orientation, and role.
        
        :param col: The column index.
        :type col: int
        :param orientation: The orientation of the header (horizontal or vertical).
        :type orientation: Qt.Orientation
        :param role: The role of the header data to retrieve.
        :type role: Qt.ItemDataRole
        :return: The header data for the given column, orientation, and role, or None if not available.
        :rtype: str | None
        """
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self._data.columns[col]
        
        return None
