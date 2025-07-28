"use client"
import { checkHealth } from "@/lib/axios/axios";
import { useEffect, useState } from "react";

export default function Page() {
  const [data, setData] = useState(null);

  useEffect(() => {
    checkHealth()
      .then((data) => setData(data))
      .catch((error) => console.error("error while fetching : ", error));
  }, []);

  return (
    <div>
      <h1>small step everyday</h1>
      <p> {JSON.stringify(data)} </p>
      
    </div>
  );
}
