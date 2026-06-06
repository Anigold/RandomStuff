let currentUser = null;

async function loadCurrentUser() {
    currentUser = await apiRequest("/me");
    console.log("Current user:", currentUser);
    return currentUser;
}

function getCurrentUser() {
    return currentUser;
}

function isSupervisorUser() {
    return currentUser?.role === "supervisor";
}

function isManagerUser() {
    return currentUser?.role === "manager";
}

function isViewerUser() {
    return currentUser?.role === "viewer";
}

function canUseSupervisorScope() {
    return Boolean(currentUser?.can_use_supervisor_scope);
}

function canManageSetupData() {
    return currentUser?.role === "supervisor";
}

function canCreateOrders() {
    return ["supervisor", "manager"].includes(currentUser?.role);
}

function canModifyOrders() {
    return ["supervisor", "manager"].includes(currentUser?.role);
}

function canUseSupervisorOrderActions() {
    return currentUser?.role === "supervisor";
}

function canEditItems() {
    return currentUser?.role === "supervisor";
}