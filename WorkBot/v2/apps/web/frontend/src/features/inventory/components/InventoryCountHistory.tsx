import type { InventoryCountDto } from "../../../api/inventoryApi";

type InventoryCountHistoryProps = {
  counts: InventoryCountDto[];
  onEditDraft: (count: InventoryCountDto) => void;
};

export function InventoryCountHistory({
  counts,
  onEditDraft,
}: InventoryCountHistoryProps) {
  if (counts.length === 0) {
    return (
      <div className="empty-card">
        <strong>No inventory counts found.</strong>
        <p>No inventory counts have been saved for this store yet.</p>
      </div>
    );
  }

  return (
    <section className="form-card-stack">
      <div className="form-card">
        <h3>Inventory history</h3>

        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Status</th>
              <th>Lines</th>
              <th>Notes</th>
              <th />
            </tr>
          </thead>

          <tbody>
            {counts.map((count) => (
              <tr key={count.id}>
                <td>{count.count_date}</td>
                <td>{count.status}</td>
                <td>{count.lines.length}</td>
                <td>{count.notes ?? ""}</td>
                <td>
                  {count.status === "draft" ? (
                    <button type="button" onClick={() => onEditDraft(count)}>
                      Edit draft
                    </button>
                  ) : (
                    <span>Submitted</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}