import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { getErrorMessage } from '../../utils/helpers';
import './CustomVisualizationBuilder.css';

interface ExcelTable {
  table_id: number;
  columns: string[];
  row_count: number;
  preview: unknown[];
  start_row: number;
  end_row: number;
}

interface ExcelSheet {
  name: string;
  tables: ExcelTable[];
  table_count: number;
}

interface ExcelStructure {
  sheets: ExcelSheet[];
  total_sheets: number;
}

interface ChartConfig {
  sheet_name: string;
  table_id: number;
  chart_type: string;
  x_column: string;
  y_columns: string[];
  title: string;
  filter?: {
    column: string;
    contains: string;
  };
}

interface CustomVisualizationBuilderProps {
  reportId: number;
  onChartCreated?: () => void;
}

const CustomVisualizationBuilder: React.FC<CustomVisualizationBuilderProps> = ({
  reportId,
  onChartCreated
}) => {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  
  const [excelStructure, setExcelStructure] = useState<ExcelStructure | null>(null);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Chart configuration state
  const [selectedSheet, setSelectedSheet] = useState<string>('');
  const [selectedTableId, setSelectedTableId] = useState<number>(0);
  const [chartType, setChartType] = useState<string>('bar');
  const [xColumn, setXColumn] = useState<string>('');
  const [yColumns, setYColumns] = useState<string[]>([]);
  const [chartTitle, setChartTitle] = useState<string>('');
  const [filterColumn, setFilterColumn] = useState<string>('');
  const [filterValue, setFilterValue] = useState<string>('');
  
  const chartTypes = [
    { value: 'bar', label: 'Bar Chart', icon: '📊' },
    { value: 'line', label: 'Line Chart', icon: '📈' },
    { value: 'pie', label: 'Pie Chart', icon: '🍰' },
    { value: 'area', label: 'Area Chart', icon: '📉' },
    { value: 'scatter', label: 'Scatter Plot', icon: '⚫' }
  ];
  
  useEffect(() => {
    loadExcelStructure();
  }, [reportId]);
  
  const loadExcelStructure = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(
        `${API_BASE_URL}/analysis/excel-structure/${reportId}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      setExcelStructure(response.data);
      
      // Auto-select first sheet
      if (response.data.sheets && response.data.sheets.length > 0) {
        setSelectedSheet(response.data.sheets[0].name);
      }
    } catch (err: unknown) {
      console.error('Failed to load Excel structure:', err);
      const errorMessage = getErrorMessage(err) || 'Failed to load Excel data structure';
      
      // Show helpful message if Excel file not found
      if (errorMessage.includes('Excel file not found') || errorMessage.includes('Generate visualizations first')) {
        setError('📊 Please generate visualizations first! The Excel file is created when you click "Generate Visualizations" button above.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreateChart = async () => {
    if (!selectedSheet || !xColumn || yColumns.length === 0 || !chartTitle) {
      setError('Please fill all required fields');
      return;
    }
    
    setCreating(true);
    setError(null);
    setSuccess(null);
    
    try {
      const chartConfig: ChartConfig = {
        sheet_name: selectedSheet,
        table_id: selectedTableId,
        chart_type: chartType,
        x_column: xColumn,
        y_columns: yColumns,
        title: chartTitle
      };
      
      // Add filter if specified
      if (filterColumn && filterValue) {
        chartConfig.filter = {
          column: filterColumn,
          contains: filterValue
        };
      }
      
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_BASE_URL}/analysis/custom-visualization/${reportId}`,
        chartConfig,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      setSuccess('Chart created successfully! 🎉');
      
      // Reset form
      setChartTitle('');
      setYColumns([]);
      setFilterColumn('');
      setFilterValue('');
      
      // Notify parent
      if (onChartCreated) {
        onChartCreated();
      }
    } catch (err: unknown) {
      setError(getErrorMessage(err) || 'Failed to create chart');
    } finally {
      setCreating(false);
    }
  };
  
  const currentSheet = excelStructure?.sheets.find(s => s.name === selectedSheet);
  const currentTable = currentSheet?.tables[selectedTableId];
  
  const toggleYColumn = (column: string) => {
    setYColumns(prev => 
      prev.includes(column) 
        ? prev.filter(c => c !== column)
        : [...prev, column]
    );
  };
  
  if (loading) {
    return (
      <div className="custom-viz-loading">
        <div className="custom-viz-loading-spinner"></div>
        <span className="custom-viz-loading-text">Loading Excel data...</span>
      </div>
    );
  }
  
  if (!excelStructure && error) {
    return (
      <div className="custom-viz-empty">
        <div className="custom-viz-alert custom-viz-alert-warning">
          <div className="custom-viz-alert-title">📊 Excel File Required</div>
          <div>{error}</div>
        </div>
        <button
          onClick={loadExcelStructure}
          className="custom-viz-retry-btn"
        >
          🔄 Retry
        </button>
      </div>
    );
  }
  
  if (!excelStructure) {
    return (
      <div className="custom-viz-empty">
        <div className="custom-viz-empty-content">
          <div className="custom-viz-empty-icon">📊</div>
          <div className="custom-viz-empty-title">No Excel Data Available</div>
          <div className="custom-viz-empty-text">
            Please generate visualizations first. The Excel file will be created automatically.
          </div>
          <button
            onClick={loadExcelStructure}
            className="custom-viz-retry-btn"
          >
            🔄 Check Again
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="custom-viz-builder">
      <div className="custom-viz-header">
        <h3 className="custom-viz-title">
          <span className="custom-viz-title-icon">📊</span>
          Custom Visualization Builder
        </h3>
        <p className="custom-viz-description">
          Create your own charts from Excel data. Choose what to visualize and how!
        </p>
      </div>
      
      {error && (
        <div className="custom-viz-alert custom-viz-alert-error">
          {error}
        </div>
      )}
      
      {success && (
        <div className="custom-viz-alert custom-viz-alert-success">
          {success}
        </div>
      )}
      
      <div className="custom-viz-form">
        {/* Sheet Selection */}
        <div className="custom-viz-field">
          <label className="custom-viz-label custom-viz-label-required">
            <span className="custom-viz-label-number">1</span>
            Select Data Sheet
          </label>
          <select
            value={selectedSheet}
            onChange={(e) => {
              setSelectedSheet(e.target.value);
              setSelectedTableId(0);
              setXColumn('');
              setYColumns([]);
            }}
            className="custom-viz-select"
          >
            {excelStructure.sheets.map(sheet => (
              <option key={sheet.name} value={sheet.name}>
                {sheet.name} ({sheet.table_count} table{sheet.table_count > 1 ? 's' : ''})
              </option>
            ))}
          </select>
        </div>
        
        {/* Table Selection (if multiple tables in sheet) */}
        {currentSheet && currentSheet.tables.length > 1 && (
          <div className="custom-viz-field">
            <label className="custom-viz-label custom-viz-label-required">
              Select Table
            </label>
            <p className="custom-viz-info-text" style={{ marginBottom: '0.75rem', fontSize: '0.875rem', color: '#2563eb' }}>
              📊 This sheet contains {currentSheet.tables.length} tables. Select which one to visualize:
            </p>
            <select
              value={selectedTableId}
              onChange={(e) => {
                setSelectedTableId(Number(e.target.value));
                setXColumn('');
                setYColumns([]);
              }}
              className="custom-viz-select"
            >
              {currentSheet.tables.map((table, idx) => (
                <option key={idx} value={idx}>
                  Table {idx + 1}: Rows {table.start_row}-{table.end_row} ({table.row_count} rows, {table.columns.length} cols)
                </option>
              ))}
            </select>
          </div>
        )}
        
        {/* Table Info (always show) */}
        {currentTable && (
          <div className="custom-viz-info">
            <p className="custom-viz-info-title">
              Selected Table: {currentTable.columns.length} columns, {currentTable.row_count} rows
              {currentSheet && currentSheet.tables.length > 1 && ` (Excel rows ${currentTable.start_row}-${currentTable.end_row})`}
            </p>
            <p className="custom-viz-info-detail">
              Columns: {currentTable.columns.join(', ')}
            </p>
          </div>
        )}
        
        {/* Chart Type */}
        <div className="custom-viz-field">
          <label className="custom-viz-label custom-viz-label-required">
            <span className="custom-viz-label-number">2</span>
            Select Chart Type
          </label>
          <div className="custom-viz-chart-grid">
            {chartTypes.map(type => (
              <button
                key={type.value}
                onClick={() => setChartType(type.value)}
                className={`custom-viz-chart-btn ${chartType === type.value ? 'active' : ''}`}
              >
                <div className="custom-viz-chart-icon">{type.icon}</div>
                <div className="custom-viz-chart-label">{type.label}</div>
              </button>
            ))}
          </div>
        </div>
        
        {/* X-Axis Column */}
        {currentTable && (
          <div className="custom-viz-field">
            <label className="custom-viz-label custom-viz-label-required">
              <span className="custom-viz-label-number">3</span>
              Select X-Axis Column
            </label>
            <select
              value={xColumn}
              onChange={(e) => setXColumn(e.target.value)}
              className="custom-viz-select"
            >
              <option value="">-- Choose column --</option>
              {currentTable.columns.map((col: string) => (
                <option key={col} value={col}>{col}</option>
              ))}
            </select>
          </div>
        )}
        
        {/* Y-Axis Columns */}
        {currentTable && (
          <div className="custom-viz-field">
            <label className="custom-viz-label custom-viz-label-required">
              <span className="custom-viz-label-number">4</span>
              Select Y-Axis Columns (can select multiple)
            </label>
            <div className="custom-viz-column-grid">
              {currentTable.columns.map((col: string) => (
                <button
                  key={col}
                  onClick={() => toggleYColumn(col)}
                  className={`custom-viz-column-btn ${yColumns.includes(col) ? 'selected' : ''}`}
                >
                  {col}
                </button>
              ))}
            </div>
            {yColumns.length > 0 && (
              <div className="custom-viz-selected-text">
                <strong>Selected:</strong> {yColumns.join(', ')}
              </div>
            )}
          </div>
        )}
        
        {/* Chart Title */}
        <div className="custom-viz-field">
          <label className="custom-viz-label custom-viz-label-required">
            <span className="custom-viz-label-number">5</span>
            Chart Title
          </label>
          <input
            type="text"
            value={chartTitle}
            onChange={(e) => setChartTitle(e.target.value)}
            placeholder="e.g., Revenue Growth Over Years"
            className="custom-viz-input"
          />
        </div>
        
        {/* Optional Filter */}
        {currentTable && (
          <div className="custom-viz-field">
            <label className="custom-viz-label">
              <span className="custom-viz-label-number">6</span>
              Filter Data (optional)
            </label>
            <div className="custom-viz-filter-grid">
              <select
                value={filterColumn}
                onChange={(e) => setFilterColumn(e.target.value)}
                className="custom-viz-select"
              >
                <option value="">-- No filter --</option>
                {currentTable.columns.map((col: string) => (
                  <option key={col} value={col}>{col}</option>
                ))}
              </select>
              {filterColumn && (
                <input
                  type="text"
                  value={filterValue}
                  onChange={(e) => setFilterValue(e.target.value)}
                  placeholder="Filter value (contains)"
                  className="custom-viz-input"
                />
              )}
            </div>
          </div>
        )}
        
        {/* Create Button */}
        <button
          onClick={handleCreateChart}
          disabled={creating || !selectedSheet || !xColumn || yColumns.length === 0 || !chartTitle}
          className="custom-viz-submit"
        >
          {creating ? (
            <>
              <span className="custom-viz-submit-spinner">⚙️</span>
              Creating Chart...
            </>
          ) : (
            <>
              🎨 Create Custom Chart
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default CustomVisualizationBuilder;
