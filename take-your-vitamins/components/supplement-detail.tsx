"use client"

import type { Supplement, CategorizedInteractions } from "@/lib/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Clock, AlertTriangle, Utensils, ChevronLeft } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"
import { getSupplementInteractions } from "@/lib/supplements"

export function SupplementDetail({ supplement }: { supplement: Supplement }) {
    console.log("Supplement Detail:", supplement)
    const [interactions, setInteractions] = useState<CategorizedInteractions | null>(null)

    useEffect(() => {
        const fetchInteractions = async () => {
            if (supplement._id) {
                 // Fetch interactions for the supplement
                const results = await getSupplementInteractions(supplement._id)
                setInteractions(results)
              } else {
                setInteractions(null)
              }
        }
        fetchInteractions()
    }, [supplement._id])

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold">{supplement.name}</h1>
                    <div className="flex items-center gap-2 mt-2">
                        <Badge variant="outline">{supplement.category}</Badge>
                        {supplement.aliases.length > 0 && (
                            <p className="text-sm text-muted-foreground">
                                Also known as: {supplement.aliases.join(", ")}
                            </p>
                        )}
                    </div>
                </div>
                <Button variant="ghost" size="sm" asChild className="mb-4">
                    <Link href="/">
                        <ChevronLeft className="mr-2 h-4 w-4" />
                        Back to Home
                    </Link>
                </Button>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Overview</CardTitle>
                    <CardDescription>General information about {supplement.name}</CardDescription>
                </CardHeader>
                <CardContent>
                    <p>{supplement.description}</p>
                </CardContent>
            </Card>

            <Tabs defaultValue="intake">
                <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="intake">
                        <Clock className="h-4 w-4 mr-2" />
                        Intake Practices
                    </TabsTrigger>
                    <TabsTrigger value="supplement-interactions">
                        <AlertTriangle className="h-4 w-4 mr-2" />
                        Supplement Interactions
                    </TabsTrigger>
                    <TabsTrigger value="food-interactions">
                        <Utensils className="h-4 w-4 mr-2" />
                        Food Interactions
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="intake" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Best Intake Practices</CardTitle>
                            <CardDescription>How to take {supplement.name} for optimal benefits</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <h3 className="font-medium mb-2 text-yellow-500">Recommended Dosage</h3>
                                <p>{supplement.intakePractices.dosage}</p>
                            </div>
                            <div>
                                <h3 className="font-medium mb-2 text-yellow-500">Timing</h3>
                                <p>{supplement.intakePractices.timing}</p>
                            </div>
                            <div>
                                <h3 className="font-medium mb-2 text-yellow-500">Special Instructions</h3>
                                <p>{supplement.intakePractices.specialInstructions}</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Supplement Interactions */}
                <TabsContent value="supplement-interactions" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Supplement Interactions</CardTitle>
                            <CardDescription>How {supplement.name} interacts with other supplements</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {(interactions?.supplementSupplementInteractions ?? []).length > 0 ? (
                                <ul className="space-y-4">
                                    {interactions?.supplementSupplementInteractions.map((interaction, index) => (
                                        <li key={index} className="border-b pb-4 last:border-0 last:pb-0">
                                            <div className="flex items-start">
                                                <div className="mr-2">
                                                    <Badge
                                                        variant={
                                                            interaction.severity?.toLowerCase() === "negative"
                                                                ? "destructive"
                                                                : interaction.severity?.toLowerCase() === "positive"
                                                                    ? "warning"
                                                                    : "outline"
                                                        }
                                                    >
                                                        {interaction.severity
                                                            ? interaction.severity.charAt(0).toUpperCase() +
                                                            interaction.severity.slice(1)
                                                            : "Unknown"}
                                                    </Badge>
                                                </div>
                                                <div>
                                                    <h3 className="font-medium">
                                                        With{" "}
                                                        {interaction.supplements
                                                            .filter((s) => s.supplementId !== supplement._id)
                                                            .map((s) => s.name)
                                                            .join(", ")}
                                                    </h3>
                                                    <p>{interaction.effect}</p>
                                                    {interaction.description && (
                                                        <p className="text-sm text-muted-foreground mt-1">
                                                            Description: {interaction.description}
                                                        </p>
                                                    )}
                                                    {interaction.recommendation && (
                                                        <p className="text-sm text-muted-foreground mt-1">
                                                            Recommendation: {interaction.recommendation}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p>No known supplement interactions for {supplement.name}.</p>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Food Interactions */}
                <TabsContent value="food-interactions" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Food Interactions</CardTitle>
                            <CardDescription>How {supplement.name} interacts with food</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {(interactions?.supplementFoodInteractions?.length ?? 0) > 0 ? (
                                <ul className="space-y-4">
                                    {interactions?.supplementFoodInteractions.map((interaction, index) => (
                                        <li key={index} className="border-b pb-4 last:border-0 last:pb-0">
                                            <div className="flex items-start">
                                                <div className="mr-2">
                                                    <Badge
                                                        variant={
                                                            interaction.effect.includes("Enhances")
                                                                ? "success"
                                                                : interaction.effect.includes("Reduces")
                                                                    ? "destructive"
                                                                    : "outline"
                                                        }
                                                    >
                                                        {interaction.effect}
                                                    </Badge>
                                                </div>
                                                <div>
                                                    <h3 className="font-medium">{interaction.foodItem || "Unknown Food"}</h3>
                                                    <p>{interaction.description}</p>
                                                    {interaction.recommendation && (
                                                        <p className="text-sm text-muted-foreground mt-1">
                                                            Description: {interaction.description}
                                                            Recommendation: {interaction.recommendation}
                                                        </p>
                                                    )}
                                                </div>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <p>No known food interactions for {supplement.name}.</p>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}