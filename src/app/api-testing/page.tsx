'use client'

import React, { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"

export default function FrappeCommandsPage() {
  const [projectName, setProjectName] = useState('')
  const [siteName, setSiteName] = useState('')
  const [output, setOutput] = useState('')

  const runCommand = async (command: string) => {
    try {
      const args = command.split(' ');
      console.log('Sending args:', args); // For debugging
      const result = await window.electronAPI.runFrappeCommand(args);
      setOutput(result);
    } catch (error) {
      setOutput(`Error: ${(error as Error).message}`);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Frappe Commands Tester</h1>
      <Card className="mb-4">
        <CardHeader>
          <CardTitle>Command Parameters</CardTitle>
          <CardDescription>Set the project and site names for the commands</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid w-full items-center gap-4">
            <div className="flex flex-col space-y-1.5">
              <Label htmlFor="projectName">Project Name</Label>
              <Input
                id="projectName"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="Enter project name"
              />
            </div>
            <div className="flex flex-col space-y-1.5">
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
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <Button onClick={() => runCommand('--all')}>Get All Projects Info</Button>
        <Button onClick={() => runCommand(`-p ${projectName} --get-sites`)}>Get Sites</Button>
        <Button onClick={() => runCommand(`-p ${projectName} --get-apps`)}>Get Apps</Button>
        <Button onClick={() => runCommand(`-p ${projectName} --get-site-apps ${siteName}`)}>Get Site Apps</Button>
        <Button onClick={() => runCommand(`-p ${projectName} --get-site-info ${siteName}`)}>Get Site Info</Button>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Command Output</CardTitle>
        </CardHeader>
        <CardContent>
          <Textarea
            value={output}
            readOnly
            className="h-64"
            placeholder="Command output will appear here"
          />
        </CardContent>
      </Card>
    </div>
  )
}

