# Public API Test Sources

The CSV files in [assets/public_api_smoke.csv](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/assets/public_api_smoke.csv) and [assets/public_api_extended.csv](/C:/Users/jonew/Downloads/Pu/Quick-Run-Regression-API/assets/public_api_extended.csv) were built from public API documentation.

## Sources

- DummyJSON docs: [https://dummyjson.com/docs](https://dummyjson.com/docs)
- JSONPlaceholder guide: [https://jsonplaceholder.typicode.com/guide/](https://jsonplaceholder.typicode.com/guide/)

## Notes

- `public_api_smoke.csv` is intended to be the safer starting point for the current app because it mostly uses `GET` endpoints.
- `public_api_extended.csv` includes broader CRUD coverage.
- Some `POST`, `PUT`, and `PATCH` rows in the extended file are based on documented endpoints but will need request-body support in the runner before they can pass consistently.
- Expected status values for mutation cases are partly inferred from the public docs and common REST behavior:
  - JSONPlaceholder `POST /posts` is documented with a created response and is treated as `201`.
  - JSONPlaceholder `PUT`, `PATCH`, and `DELETE` examples are treated as `200`.
  - DummyJSON add endpoints are treated as `201`, while update and delete endpoints are treated as `200`.
