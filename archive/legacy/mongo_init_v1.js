// UrbanLens MongoDB initialization / validation V1
// Run: mongosh "$MONGODB_URI" urbanlens mongo_init.js

db.runCommand({ ping: 1 });

const collections = [
  "cities","city_aliases","city_provider_identities","countries",
  "country_metrics","gdp_country_metrics","cost_of_living","universities",
  "university_rankings","weather_observations","weather_forecasts_wmo",
  "air_quality_observations_global_weather","air_quality_observations_who",
  "source_registry"
];

print("Collections:");
collections.forEach(c => print(` - ${c}: ${db.getCollection(c).estimatedDocumentCount()}`));

print("\nCanonical identity checks:");
printjson({
  cities: db.cities.countDocuments({city_id: {$exists:true}}),
  cities_without_city_id: db.cities.countDocuments({city_id: {$exists:false}}),
  duplicate_city_ids: db.cities.aggregate([
    {$group:{_id:"$city_id", n:{$sum:1}}},
    {$match:{n:{$gt:1}}},
    {$count:"duplicates"}
  ]).toArray()
});

print("\nProvider identity check:");
printjson(db.city_provider_identities.aggregate([
  {$group:{_id:{provider:"$provider", provider_location_id:"$provider_location_id"}, n:{$sum:1}}},
  {$match:{n:{$gt:1}}},
  {$count:"duplicate_provider_ids"}
]).toArray());

print("\nDone. Review counts above before connecting application services.");
