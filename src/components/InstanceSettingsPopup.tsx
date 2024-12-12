import React, { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import { 
AlertDialog, 
AlertDialogAction, 
AlertDialogCancel, 
AlertDialogContent, 
AlertDialogDescription, 
AlertDialogFooter, 
AlertDialogHeader, 
AlertDialogTitle, 
AlertDialogTrigger 
} from '@/components/ui/alert-dialog'

interface FrappeInstance {
  projectName: string
  ports: string[]
  status: string
}

interface InstanceSettingsPopupProps {
  instance: FrappeInstance
  onClose: () => void
  onReload: () => void
}

export function InstanceSettingsPopup({ instance, onClose, onReload }: InstanceSettingsPopupProps) {
  const [backupBeforeDelete, setBackupBeforeDelete] = useState(false)

  const handleAddApp = async () => {
    // Implement add app functionality
    console.log('Add app')
  }

  const handleAddSite = async () => {
    // Implement add site functionality
    console.log('Add site')
  }

  const handleDeleteInstance = async () => {
    if (typeof window !== 'undefined' && window.electronAPI) {
      await window.electronAPI.deleteInstance(instance.projectName, backupBeforeDelete)
      onReload()
      onClose()
    } else {
      console.log('Electron API not available')
    }
  }

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{instance.projectName} Settings</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="port" className="text-right">
              Port
            </Label>
            <Input id="port" value={instance.ports[0]} className="col-span-3" readOnly />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="status" className="text-right">
              Status
            </Label>
            <Input id="status" value={instance.status} className="col-span-3" readOnly />
          </div>
          {/* Add more instance details here */}
        </div>
        <DialogFooter className="flex justify-between">
          <div>
            <Button onClick={handleAddApp} className="mr-2">Add App</Button>
            <Button onClick={handleAddSite}>Add Site</Button>
          </div>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" className='bg-red-600 hover:bg-red-700'>Delete Instance</Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                <AlertDialogDescription>
                  This action cannot be undone. This will permanently delete the
                  instance and all associated data.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="backup"
                  checked={backupBeforeDelete}
                  onCheckedChange={(checked) => setBackupBeforeDelete(checked as boolean)}
                />
                <label
                  htmlFor="backup"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Backup before deleting
                </label>
              </div>
              <AlertDialogFooter>
                <AlertDialogCancel>Cancel</AlertDialogCancel>
                <AlertDialogAction onClick={handleDeleteInstance} className="bg-red-600 hover:bg-red-700 text-white">Delete</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

