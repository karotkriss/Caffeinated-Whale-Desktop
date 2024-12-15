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
    <div className="flex min-h-screen flex-col items-center justify-between flex-1">
      <div className="z-50 font-mono text-sm md:p-10 rounded-tl-2xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 bg-opacity-25 dark:bg-opacity-25 sflex flex-col gap-2 flex-1 w-full overflow-y-auto">

        <div className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {instances.map((instance: FrappeInstance, index: number) => (
            <InstanceCard
              key={index}
              projectName={instance.projectName}
              sites={instance.sites}
              apps={instance.apps}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

