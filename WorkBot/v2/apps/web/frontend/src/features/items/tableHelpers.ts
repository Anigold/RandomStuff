import type { ItemDto } from "../../api/itemsApi";

export type ItemSortKey =
  | "name"
  | "category"
  | "subcategory"
  | "countUnit"
  | "status";

export type ItemSortDirection = "asc" | "desc";

export type ItemSortState = {
  key: ItemSortKey;
  direction: ItemSortDirection;
};

export type ItemStatusFilter = "all" | "active" | "inactive";

export function normalize(value: unknown): string {
  return String(value ?? "").trim().toLowerCase();
}

function compareText(
  left: string | null | undefined,
  right: string | null | undefined,
): number {
  return normalize(left).localeCompare(normalize(right));
}

function compareBoolean(left: boolean, right: boolean): number {
  if (left === right) {
    return 0;
  }

  return left ? -1 : 1;
}

export function getCountUnitLabel(item: ItemDto): string {
  const quantity = item.count_unit_quantity;
  const measure = item.count_unit_measure;

  if (quantity && measure) {
    return `${quantity} ${measure}`;
  }

  if (quantity) {
    return quantity;
  }

  if (measure) {
    return measure;
  }

  return "—";
}

/**
 * Normalizes values for item search while preserving meaningful search symbols.
 *
 * Examples:
 * - "Banana - Fresh" -> "banana fresh"
 * - "2% Milk" -> "2% milk"
 * - "12/Case" -> "12 case"
 */
export function normalizeSearchValue(value: unknown): string {
  return normalize(value)
    .replace(/[^a-z0-9%]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

export function getSearchTokens(value: unknown): string[] {
  return Array.from(
    new Set(
      normalizeSearchValue(value)
        .split(" ")
        .map((token) => token.trim())
        .filter(Boolean),
    ),
  );
}

export function getItemSearchTokens(item: ItemDto): string[] {
  return [
    item.id,
    item.name,
    item.category,
    item.subcategory,
    item.count_unit_quantity,
    item.count_unit_measure,
    item.is_active ? "active" : "inactive",
  ].flatMap(getSearchTokens);
}

export function getSearchText(item: ItemDto): string {
  return getItemSearchTokens(item).join(" ");
}

export function itemMatchesSearchTokens(
  item: ItemDto,
  searchTokens: string[],
): boolean {
  if (searchTokens.length === 0) {
    return true;
  }

  const itemTokens = getItemSearchTokens(item);

  return searchTokens.every((searchToken) =>
    itemTokens.some((itemToken) =>
      itemTokenMatchesSearchToken(itemToken, searchToken),
    ),
  );
}

function itemTokenMatchesSearchToken(
  itemToken: string,
  searchToken: string,
): boolean {
  if (isStrictSearchToken(searchToken)) {
    return itemToken === searchToken;
  }

  return itemToken.includes(searchToken);
}

function isStrictSearchToken(token: string): boolean {
  return /[^a-z]/.test(token);
}

export function getUniqueSortedValues(
  items: ItemDto[],
  selector: (item: ItemDto) => string | null | undefined,
): string[] {
  return Array.from(
    new Set(
      items
        .map(selector)
        .map((value) => value?.trim())
        .filter((value): value is string => Boolean(value)),
    ),
  ).sort((left, right) => left.localeCompare(right));
}

export function getSortLabel(
  key: ItemSortKey,
  sortState: ItemSortState,
): string {
  if (sortState.key !== key) {
    return "";
  }

  return sortState.direction === "asc" ? " ↑" : " ↓";
}

export function sortItems(
  items: ItemDto[],
  sortState: ItemSortState,
): ItemDto[] {
  return [...items].sort((left, right) => {
    let result = 0;

    switch (sortState.key) {
      case "name":
        result = compareText(left.name, right.name);
        break;

      case "category":
        result = compareText(left.category, right.category);
        break;

      case "subcategory":
        result = compareText(left.subcategory, right.subcategory);
        break;

      case "countUnit":
        result = compareText(getCountUnitLabel(left), getCountUnitLabel(right));
        break;

      case "status":
        result = compareBoolean(left.is_active, right.is_active);
        break;
    }

    return sortState.direction === "asc" ? result : -result;
  });
}