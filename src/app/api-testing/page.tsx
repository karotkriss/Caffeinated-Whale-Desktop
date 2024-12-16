'use client'

import React, { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"

export default function FrappeCommandsPage() {
  const [projectName, setProjectName] = useState('')
  const [siteName, setSiteName] = useState('')
  const [output, setOutput] = useState('')

  const runCommand = async (command: string, ...additionalArgs: string[]) => {
    try {
      const args = [command]
      if (projectName) args.push('-p', projectName)
      if (additionalArgs.length > 0) args.push(...additionalArgs)
      const result = await window.electronAPI.runFrappeCommand(args)
      setOutput(result)
    } catch (error) {
      setOutput(`Error: ${error.message}`)
    }
  }

  return (
    <div className="z-50 z-50 container mx-auto p-4">
      <h1 className="z-50 text-2xl font-bold mb-4">Frappe Commands Tester</h1>
      <Card className="z-50 mb-4">
        <CardHeader>
          <CardTitle>Command Parameters</CardTitle>
          <CardDescription>Set the project and site names for the commands</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="z-50 grid w-full items-center gap-4">
            <div className="z-50 flex flex-col space-y-1.5">
              <Label htmlFor="projectName">Project Name</Label>
              <Input
                id="projectName"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="Enter project name"
              />
            </div>
            <div className="z-50 flex flex-col space-y-1.5">
              <Label htmlFor="siteName">Site Name</Label>
              <Input
                id="siteName"
                value={siteName}
                onChange={(e) => setSiteName(e.target.value)}
                placeholder="Enter site name"
              />
            </div>
          </div>
        </CardContent>
      </Card>
      <div className="z-50 grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <Button onClick={() => runCommand('--all')}>Get All Projects Info</Button>
        <Button onClick={() => runCommand('-p', projectName, '--get-sites')}>Get Sites</Button>
        <Button onClick={() => runCommand('--get-apps')}>Get Apps</Button>
        <Button onClick={() => runCommand('--get-site-app', siteName)}>Get Site Apps</Button>
        <Button onClick={() => runCommand('--get-site-info', siteName)}>Get Site Info</Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Command Output</CardTitle>
        </CardHeader>
        <CardContent>
          <Textarea
            value={output}
            readOnly
            className="z-100 h-64"
            placeholder="Command output will appear here"
          />
        </CardContent>
      </Card>
    </div>
  )
}

