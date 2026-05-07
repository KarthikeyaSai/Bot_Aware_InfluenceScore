export interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
  align?: 'left' | 'right' | 'center';
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  rowKey: (row: T) => string;
  onRowClick?: (row: T) => void;
}

export function DataTable<T>({ columns, data, rowKey, onRowClick }: DataTableProps<T>) {
  return (
    <div className="w-full overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col.key as string}
                className={`
                  text-xs font-medium uppercase tracking-[0.06em]
                  text-text-secondary pb-3 border-b border-border
                  ${col.align === 'right' ? 'text-right' : 'text-left'}
                `}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr
              key={rowKey(row)}
              onClick={() => onRowClick?.(row)}
              className={`
                h-[52px] border-b border-border-subtle
                text-text-secondary
                transition-colors duration-fast
                hover:bg-bg-elevated
                ${onRowClick ? 'cursor-pointer' : ''}
              `}
            >
              {columns.map((col, i) => (
                <td
                  key={col.key as string}
                  className={`
                    py-0 pr-4
                    ${i === 0 ? 'font-medium text-text-primary' : ''}
                    ${col.align === 'right' ? 'text-right' : ''}
                  `}
                >
                  {col.render
                    ? col.render(row)
                    : String((row as Record<string, unknown>)[col.key as string] ?? '—')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
