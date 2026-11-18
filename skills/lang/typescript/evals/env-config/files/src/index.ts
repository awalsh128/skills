const API_URL = "https://api.weather.example.com/v2";
const API_KEY = "sk_live_51HxQ2example";

async function forecast(city: string): Promise<unknown> {
  const res = await fetch(API_URL + "/forecast?city=" + city + "&key=" + API_KEY);
  if (!res.ok) throw new Error(`forecast failed: ${res.status}`);

  return res.json();
}

const city = process.argv[2] ?? "Seattle";
console.log(await forecast(city));
