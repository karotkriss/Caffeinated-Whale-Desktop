'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

interface FrappeInstance {
  projectName: string
  ports: string[]
  status: string
}

export default function Home() {
  const [instances, setInstances] = useState<FrappeInstance[]>([])
  const [projectName, setProjectName] = useState<string>('')
  const [siteName, setSiteName] = useState<string>('')

  useEffect(() => {
    loadInstances()
  }, [])

  const loadInstances = async () => {
    if (typeof window !== 'undefined' && window.electronAPI) {
      const loadedInstances = await window.electronAPI.listFrappeInstances()
      setInstances(loadedInstances)
    } else {
      console.log('Electron API not available')
      // You can set some mock data here for development in the browser
      setInstances([
        { projectName: 'Mock Project', ports: ['8000'], status: 'running' }
      ])
    }
  }

  const handleCreateInstance = async () => {
    if (typeof window !== 'undefined' && window.electronAPI) {
      const port = await window.electronAPI.getAvailablePort(8000)
      const instanceConfig = {
        projectName,
        siteName,
        port
      }
      await window.electronAPI.createFrappeInstance(instanceConfig)
      await loadInstances()
    } else {
      console.log('Electron API not available')
      // You can add some mock behavior here for development in the browser
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-between flex-1">
      <div className="z-10 w-full items-center justify-between font-mono text-sm md:p-10 rounded-tl-2xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 flex flex-col gap-2 flex-1 w-full h-full">
        <div className="flex gap-2">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {instances.map((instance: FrappeInstance, index: number) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle>{instance.projectName}</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Port: {instance.ports[0] || 'N/A'}</p>
                <p>Status: {instance.status}</p>
              </CardContent>
            </Card>
          ))}
        </div>
        </div>
      </div>
    </div>
  )
}