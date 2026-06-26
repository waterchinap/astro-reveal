// utils/paginate.js
export function pagearr(arr, pageSize) {
  return Array.from(
    { length: Math.ceil(arr.length / pageSize) },
    (_, index) => arr.slice(index * pageSize, (index + 1) * pageSize)
  );
}
