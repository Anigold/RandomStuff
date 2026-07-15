import { useState } from "react";

import {
  createVendor,
  deleteVendor,
  updateVendor,
  type VendorDto,
  type VendorWriteDto,
} from "../../../api/vendorsApi";
import { useAccessToken } from "../../auth/hooks/useAccessTokens";
import { useStoreScope } from "../../stores/hooks/useStoreScope";
import { VendorActionsModal } from "../components/VendorActionsModal";
import { VendorFormModal } from "../components/VendorFormModal";
import { VendorsTable } from "../components/VendorsTable";
import { useVendorsManagement } from "../hooks/useVendorsManagement";

type FormMode =
  | { type: "closed" }
  | { type: "create" }
  | { type: "edit"; vendor: VendorDto };

export function VendorsManagementPage() {
  const accessToken = useAccessToken();
  const { activeScopeId } = useStoreScope();
  const {
    vendors,
    stores,
    isLoadingVendors,
    vendorErrorMessage,
    canManageVendors,
    reloadVendors,
  } = useVendorsManagement();

  const [formMode, setFormMode] = useState<FormMode>({ type: "closed" });
  const [selectedVendor, setSelectedVendor] = useState<VendorDto | null>(null);
  const [actionErrorMessage, setActionErrorMessage] = useState<string | null>(
    null,
  );

  async function handleCreateVendor(vendor: VendorWriteDto) {
    if (!activeScopeId) {
      throw new Error("Select a supervisor scope before creating a vendor.");
    }

    await createVendor({
      accessToken,
      scopeId: activeScopeId,
      vendor,
    });

    await reloadVendors();
    setFormMode({ type: "closed" });
  }

  async function handleUpdateVendor(vendor: VendorWriteDto) {
    if (!activeScopeId) {
      throw new Error("Select a supervisor scope before updating a vendor.");
    }

    if (formMode.type !== "edit") {
      throw new Error("No vendor is selected for editing.");
    }

    await updateVendor({
      accessToken,
      scopeId: activeScopeId,
      vendorId: formMode.vendor.id,
      vendor,
    });

    await reloadVendors();
    setSelectedVendor(null);
    setFormMode({ type: "closed" });
  }


  async function handleDeactivateVendor(vendor: VendorDto) {
    if (!activeScopeId) {
      setActionErrorMessage(
        "Select a supervisor scope before deactivating a vendor.",
      );
      return;
    }

    const confirmed = window.confirm(
      `Deactivate ${vendor.name}? This will hide it from normal vendor workflows but preserve historical records.`,
    );

    if (!confirmed) {
      return;
    }

    setActionErrorMessage(null);

    try {
      await deleteVendor({
        accessToken,
        scopeId: activeScopeId,
        vendorId: vendor.id,
      });

      await reloadVendors();
      setSelectedVendor(null);
    } catch (error) {
      setActionErrorMessage(
        error instanceof Error ? error.message : "Unable to deactivate vendor.",
      );
    }
  }



  function vendorToWriteDto(
    vendor: VendorDto,
    overrides: Partial<VendorWriteDto> = {},
    ): VendorWriteDto {
    return {
        name: vendor.name,
        is_active: vendor.is_active,
        order_format: vendor.order_format ?? "",
        special_notes: vendor.special_notes ?? "",
        min_order_value: String(vendor.min_order_value ?? "0"),
        min_order_cases: vendor.min_order_cases ?? 0,
        internal_contacts: vendor.internal_contacts ?? [],
        ordering: vendor.ordering ?? {
        method: [],
        email: "",
        portal_url: "",
        phone_number: "",
        schedule: [],
        },
        store_references: vendor.store_references ?? [],
        ...overrides,
    };
    }


    async function handleActivateVendor(vendor: VendorDto) {
        if (!activeScopeId) {
            setActionErrorMessage(
            "Select a supervisor scope before reactivating a vendor.",
            );
            return;
        }

        setActionErrorMessage(null);

        try {
            await updateVendor({
            accessToken,
            scopeId: activeScopeId,
            vendorId: vendor.id,
            vendor: vendorToWriteDto(vendor, {
                is_active: true,
            }),
            });

            await reloadVendors();
            setSelectedVendor(null);
        } catch (error) {
            setActionErrorMessage(
            error instanceof Error ? error.message : "Unable to reactivate vendor.",
            );
        }
        }

  if (!canManageVendors) {
    return (
      <section className="page-stack">
        <header className="page-header">
          <div>
            <h2>Vendors</h2>
            <p>Manage vendor records and ordering information.</p>
          </div>
        </header>

        <div className="info-card">
          <strong>Supervisor scope required.</strong>
          <p>Switch to the supervisor operating scope to manage vendors.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <h2>Vendors</h2>
          <p>Manage vendor records, contacts, ordering, and store references.</p>
        </div>

        <button
          type="button"
          onClick={() => {
            setActionErrorMessage(null);
            setSelectedVendor(null);
            setFormMode({ type: "create" });
          }}
        >
          Add vendor
        </button>
      </header>

      {actionErrorMessage && (
        <div className="error-card" role="alert">
          {actionErrorMessage}
        </div>
      )}

      {isLoadingVendors && <p>Loading vendors...</p>}

      {vendorErrorMessage && (
        <div className="error-card" role="alert">
          <strong>Unable to load vendors.</strong>
          <p>{vendorErrorMessage}</p>
        </div>
      )}

      {!isLoadingVendors && !vendorErrorMessage && vendors.length === 0 && (
        <div className="empty-card">
          <strong>No vendors found.</strong>
          <p>Add the first vendor to begin managing vendor data.</p>
        </div>
      )}

      {!isLoadingVendors && !vendorErrorMessage && vendors.length > 0 && (
        <VendorsTable
          vendors={vendors}
          onSelectVendor={(vendor) => {
            setActionErrorMessage(null);
            setSelectedVendor(vendor);
            setFormMode({ type: "closed" });
          }}
        />
      )}

      {selectedVendor && formMode.type === "closed" && (
        <VendorActionsModal
        vendor={selectedVendor}
        stores={stores}
        onClose={() => setSelectedVendor(null)}
        onEdit={(vendor) => {
            setSelectedVendor(null);
            setFormMode({ type: "edit", vendor });
        }}
        onDeactivate={handleDeactivateVendor}
        onActivate={handleActivateVendor}
        />
      )}

      {formMode.type === "create" && (
        <VendorFormModal
          stores={stores}
          title="Add vendor"
          submitLabel="Create vendor"
          onSubmit={handleCreateVendor}
          onClose={() => setFormMode({ type: "closed" })}
        />
      )}

      {formMode.type === "edit" && (
        <VendorFormModal
          initialVendor={formMode.vendor}
          stores={stores}
          title="Edit vendor"
          submitLabel="Save vendor"
          onSubmit={handleUpdateVendor}
          onClose={() => setFormMode({ type: "closed" })}
        />
      )}
    </section>
  );
}