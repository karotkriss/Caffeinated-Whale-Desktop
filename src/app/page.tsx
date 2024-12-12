'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Settings, ExternalLink, HardDrive, Activity } from 'lucide-react'
import { InstanceSettingsPopup } from '@/components/InstanceSettingsPopup'

interface FrappeInstance {
  projectName: string
  ports: string[]
  status: string
}

export default function Home() {
  const [instances, setInstances] = useState<FrappeInstance[]>([])
  const [selectedInstance, setSelectedInstance] = useState<FrappeInstance | null>(null)

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
        { projectName: 'Mock Project', ports: ['8000'], status: 'running' },
        { projectName: 'Test Instance', ports: ['8001'], status: 'stopped' }
      ])
    }
  }

  const handleOpenSettings = (instance: FrappeInstance) => {
    setSelectedInstance(instance)
  }

  const handleCloseSettings = () => {
    setSelectedInstance(null)
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-between flex-1">
      <div className="z-10 w-full items-center justify-between font-mono text-sm md:p-10 rounded-tl-2xl border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 flex flex-col gap-2 flex-1 w-full h-full">
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {instances.map((instance: FrappeInstance, index: number) => (
            <Card key={index} className="relative">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium pr-4">
                  {instance.projectName}
                </CardTitle>
                <div className="flex space-x-2">
                  <Button variant="ghost" size="icon" asChild>
                    <a href={`http://localhost:${instance.ports[0]}`} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => handleOpenSettings(instance)}>
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex justify-between items-center mt-4">
                  <div className="flex items-center space-x-2">
                    <HardDrive className="h-4 w-4 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">{instance.ports[0]}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">{instance.status}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
      {selectedInstance && (
        <InstanceSettingsPopup
          instance={selectedInstance}
          onClose={handleCloseSettings}
          onReload={loadInstances}
        />
      )}
    </div>
  )
}

