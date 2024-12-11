'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

interface FrappeInstance {
  projectName: string
  siteName: string
  port: number
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
        { projectName: 'Mock Project', siteName: 'mock.site', port: 8000 }
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
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-8">Caffeinated Whale Desktop</h1>
        
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Create New Frappe Instance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid w-full items-center gap-4">
              <div className="flex flex-col space-y-1.5">
                <Label htmlFor="projectName">Project Name</Label>
                <Input id="projectName" value={projectName} onChange={(e) => setProjectName(e.target.value)} />
              </div>
              <div className="flex flex-col space-y-1.5">
                <Label htmlFor="siteName">Site Name</Label>
                <Input id="siteName" value={siteName} onChange={(e) => setSiteName(e.target.value)} />
              </div>
              <Button onClick={handleCreateInstance}>Create Instance</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Frappe Instances</CardTitle>
          </CardHeader>
          <CardContent>
            {instances.map((instance: FrappeInstance, index: number) => (
              <div key={index} className="mb-4">
                <h3 className="text-lg font-semibold">{instance.projectName}</h3>
                <p>Site: {instance.siteName}</p>
                <p>Port: {instance.port}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </main>
  )
}

