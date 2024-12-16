import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Sheet, SheetContent, SheetDescription, SheetFooter, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Play, RefreshCcw, Square } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface InstanceCardProps {
    projectName: string
    sites: string[]
    apps: string[]
}

export function InstanceCard({ projectName, sites, apps }: InstanceCardProps) {
    const [isRunning, setIsRunning] = useState(false)
    const [openSheet, setOpenSheet] = useState(false)

    const toggleInstance = () => {
        setIsRunning(!isRunning)
        // Here you would typically call an API to start/stop the instance
    }

    return (
        <Card className="relative">
            <div className="flex justify-between">
                <CardHeader className='flex justify-between'>
                    <CardTitle>{projectName}</CardTitle>
                    {/* ToDo: implement detectiion for production or development environment */}
                    <CardDescription>Development Instance</CardDescription>
                </CardHeader>
                <CardHeader>
                    <div className="flex justify-between gap-2">
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button variant={isRunning ? "destructive" : "ghost"} onClick={toggleInstance}>
                                        {isRunning ? <Square /> : <Play />}
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                    {isRunning ? "Stop Container in Stack" : "Start Containers in Stack"}
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                        <Button variant="ghost">
                            <RefreshCcw />
                        </Button>
                    </div>
                </CardHeader>
            </div>
            <CardContent>
                <div className="grid w-full items-center gap-4 flex-1">
                    <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="sites">Sites</Label>
                        <div className="flex flex-wrap gap-2">
                            {sites.map((site, index) => (
                                <Badge key={index} variant="secondary">{site}</Badge>
                            ))}
                        </div>
                    </div>
                    <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="apps">Apps</Label>
                        <div className="flex flex-wrap gap-2">
                            {apps.map((app, index) => (
                                <Badge key={index} variant="outline">{app}</Badge>
                            ))}
                        </div>
                    </div>
                </div>
            </CardContent>
            <CardFooter className="flex justify-between sticky buttom-0">
                <Sheet open={openSheet} onOpenChange={setOpenSheet}>
                    <SheetTrigger asChild>
                        <Button variant="outline">Settings</Button>
                    </SheetTrigger>
                    <SheetContent>
                        <SheetHeader>
                            <SheetTitle>{projectName} Settings</SheetTitle>
                            <SheetDescription>
                                Configure the settings for this Frappe instance.
                            </SheetDescription>
                        </SheetHeader>
                        <div className="grid gap-4 py-4">
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="name" className="text-right">
                                    Name
                                </Label>
                                <Input id="name" value={projectName} className="col-span-3" />
                            </div>
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="port" className="text-right">
                                    Port
                                </Label>
                                <Input id="port" value="8000" className="col-span-3" />
                            </div>
                        </div>
                        <SheetFooter>
                            <Button type="submit">Save changes</Button>
                        </SheetFooter>
                    </SheetContent>
                </Sheet>
            </CardFooter>
        </Card>
    )
}

