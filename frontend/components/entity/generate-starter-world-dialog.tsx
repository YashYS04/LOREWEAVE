"use client";

import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { Loader2, Sparkles, CheckCircle2 } from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { universeService } from "@/services/universe.service";

interface GenerateStarterWorldDialogProps {
  universeId: string;
  slug: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const STEPS = [
  "Creating Characters...",
  "Creating Locations...",
  "Creating Organizations...",
  "Creating Objects...",
  "Creating Rules...",
  "Forging Relationships...",
  "Building Timeline...",
  "Preparing AI Context...",
];

export function GenerateStarterWorldDialog({
  universeId,
  open,
  onOpenChange,
}: GenerateStarterWorldDialogProps) {
  const queryClient = useQueryClient();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const handleGenerate = async () => {
    setIsGenerating(true);
    
    // Simulate steps for UI progression while backend does its work quickly
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 400);

    try {
      await universeService.generateStarterWorld(universeId);
      
      // Fast forward steps on success
      clearInterval(interval);
      setCurrentStep(STEPS.length - 1);
      
      // Invalidate all related caches
      queryClient.invalidateQueries({ queryKey: ["characters", universeId] });
      queryClient.invalidateQueries({ queryKey: ["locations", universeId] });
      queryClient.invalidateQueries({ queryKey: ["organizations", universeId] });
      queryClient.invalidateQueries({ queryKey: ["worldObjects", universeId] });
      queryClient.invalidateQueries({ queryKey: ["worldRules", universeId] });
      queryClient.invalidateQueries({ queryKey: ["relationships", universeId] });
      queryClient.invalidateQueries({ queryKey: ["timelineEvents", universeId] });
      
      setIsSuccess(true);
    } catch (error) {
      console.error("Failed to generate starter world:", error);
      clearInterval(interval);
      setIsGenerating(false);
      setCurrentStep(0);
      // In a real app we would show a toast here
    }
  };

  const handleClose = () => {
    if (!isGenerating) {
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        {!isGenerating && !isSuccess ? (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Generate Starter World?
              </DialogTitle>
              <DialogDescription className="pt-4 space-y-4">
                <p>
                  We&apos;ll create a complete starter world including characters, locations, organizations, objects, rules, relationships, and timeline events.
                </p>
                <p>
                  This only affects this universe and provides a rich environment to explore the AI, Knowledge Graph, and Timeline features immediately.
                </p>
                <p className="text-destructive font-medium text-sm">
                  This cannot overwrite existing data.
                </p>
              </DialogDescription>
            </DialogHeader>
            <DialogFooter className="mt-6">
              <Button variant="ghost" onClick={handleClose}>
                Cancel
              </Button>
              <Button onClick={handleGenerate} className="gap-2">
                <Sparkles className="h-4 w-4" />
                Generate
              </Button>
            </DialogFooter>
          </>
        ) : isSuccess ? (
          <>
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2 text-primary">
                <CheckCircle2 className="h-5 w-5" />
                Starter World Ready
              </DialogTitle>
              <DialogDescription className="pt-2">
                Your universe is ready to explore! The Knowledge Graph has been connected and the Timeline established.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter className="mt-6">
              <Button onClick={() => onOpenChange(false)} className="w-full">
                Explore World
              </Button>
            </DialogFooter>
          </>
        ) : (
          <div className="py-8 flex flex-col items-center justify-center text-center space-y-6">
            <Loader2 className="h-10 w-10 animate-spin text-primary" />
            <div className="space-y-2">
              <h3 className="font-semibold text-lg">Weaving Lore...</h3>
              <p className="text-muted-foreground text-sm min-h-[1.5rem] transition-all">
                {STEPS[currentStep]}
              </p>
            </div>
            
            <div className="w-full bg-secondary rounded-full h-1.5 overflow-hidden">
              <div 
                className="bg-primary h-full transition-all duration-300 ease-out"
                style={{ width: `${((currentStep + 1) / STEPS.length) * 100}%` }}
              />
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
