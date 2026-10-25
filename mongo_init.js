// Apply indexes only after manually selecting the intended database.
// This script never drops collections or modifies documents.
const numericKeys = new Set(["worldcities_id", "period", "year", "ranking_year", "rank", "source_row"]);
const dateKeys = new Set(["observed_at", "forecast_for"]);

function naturalKeyOptions(fields) {
  const partialFilterExpression = {};
  fields.forEach((field) => {
    if (numericKeys.has(field)) {
      partialFilterExpression[field] = { $type: "number" };
    } else if (dateKeys.has(field)) {
      partialFilterExpression[field] = { $type: "date" };
    } else {
      partialFilterExpression[field] = { $type: "string", $gt: "" };
    }
  });
  return { unique: true, partialFilterExpression };
}

const indexes = [
  ["cities", { city_id: 1 }, naturalKeyOptions(["city_id"])],
  ["cities", { worldcities_id: 1 }, naturalKeyOptions(["worldcities_id"])],
  ["city_aliases", { city_id: 1, normalized_alias: 1 }, naturalKeyOptions(["city_id", "normalized_alias"])],
  ["city_provider_identities", { provider: 1, provider_location_id: 1 }, naturalKeyOptions(["provider", "provider_location_id"])],
  ["countries", { country_id: 1 }, naturalKeyOptions(["country_id"])],
  ["countries", { iso2: 1 }, naturalKeyOptions(["iso2"])],
  ["countries", { iso3: 1 }, naturalKeyOptions(["iso3"])],
  ["country_metrics", { country_id: 1, metric: 1, period: 1 }, naturalKeyOptions(["country_id", "metric", "period"])],
  ["gdp_country_metrics", { country_id: 1, metric: 1, period: 1 }, naturalKeyOptions(["country_id", "metric", "period"])],
  ["cost_of_living", { city_id: 1, metric: 1, observed_at: 1, source_id: 1, source_record_key: 1 }, {}],
  ["universities", { university_id: 1 }, naturalKeyOptions(["university_id"])],
  ["university_rankings", { university_id: 1, ranking_metric: 1, ranking_year: 1, source_record_key: 1 }, {}],
  ["weather_observations", { city_id: 1, provider: 1, observed_at: 1, source_row: 1 }, naturalKeyOptions(["city_id", "provider", "observed_at", "source_row"])],
  ["weather_forecasts_wmo", { city_id: 1, provider: 1, forecast_for: 1 }, naturalKeyOptions(["city_id", "provider", "forecast_for"])],
  ["air_quality_observations_global_weather", { city_id: 1, provider: 1, observed_at: 1, source_row: 1 }, naturalKeyOptions(["city_id", "provider", "observed_at", "source_row"])],
  ["air_quality_observations_who", { city_id: 1, source: 1, year: 1, source_row: 1 }, naturalKeyOptions(["city_id", "source", "year", "source_row"])],
  ["source_registry", { source_id: 1 }, naturalKeyOptions(["source_id"])],
];

indexes.forEach(([collectionName, keys, options]) => {
  db.getCollection(collectionName).createIndex(keys, options);
  print(`Prepared index: ${collectionName} ${JSON.stringify(keys)}`);
});