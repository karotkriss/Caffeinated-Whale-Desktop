"use client"

import { useState, useEffect } from 'react'
import { InstanceCard } from '@/components/InstanceCard'

interface FrappeInstance {
  projectName: string
  sites: string[]
  apps: string[]
}

export default function Home() {
  const [instances, setInstances] = useState<FrappeInstance[]>([])

  useEffect(() => {
    // In a real application, you would fetch this data from your backend
    const mockInstances: FrappeInstance[] = [
      {
        projectName: "Project A",
        sites: ["site1.localhost", "site2.localhost"],
        apps: ["frappe", "erpnext", "hrms"]
      },
      {
        projectName: "Project B",
        sites: ["site3.localhost"],
        apps: ["frappe", "erpnext"]
      }
    ]
    setInstances(mockInstances)
  }, [])

  return (
    <main className="flex min-h-screen flex-col justify-between p-24">
      <div className="z-10 w-full max-w-5xl justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8">Caffeinated Whale Desktop</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {instances.map((instance, index) => (
            <InstanceCard
              key={index}
              projectName={instance.projectName}
              sites={instance.sites}
              apps={instance.apps}
            />
          ))}
        </div>
      </div>
    </main>
  )
}

