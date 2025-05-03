"use client"

import type { Supplement, CategorizedInteractions } from "@/lib/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Clock, AlertTriangle, Utensils, ChevronLeft, Info, FileText, Plus } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"
import { getSupplementInteractions } from "@/lib/supplements"
import { PageContainer } from "@/components/page-container"
import { PageHeader } from "@/components/page-header"
import { useAuth } from "@/contexts/auth-context"

export function SupplementDetail({ supplement }: { supplement: Supplement }) {
    console.log("Supplement Detail:", supplement)
    const [interactions, setInteractions] = useState<CategorizedInteractions | null>(null)
    const { user } = useAuth()

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
        <PageContainer withGradient>
            <PageHeader
                title={supplement.name}
                description={
                    <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className="bg-primary/10 hover:bg-primary/20">{supplement.category}</Badge>
                        {supplement.aliases.length > 0 && (
                            <p className="text-sm text-muted-foreground">
                                Also known as: {supplement.aliases.join(", ")}
                            </p>
                        )}
                    </div>
                }
                actions={
                    <div className="flex gap-3">
                        <Button variant="ghost" size="sm" asChild>
                            <Link href="/">
                                <ChevronLeft className="mr-2 h-4 w-4" />
                                Back to Home
                            </Link>
                        </Button>
                        {user && (
                            <Button size="sm" asChild>
                                <Link href={`/dashboard/tracker/add?supplement=${supplement._id}`}>
                                    <Plus className="mr-2 h-4 w-4" />
                                    Track This
                                </Link>
                            </Button>
                        )}
                    </div>
                }
            />

            <Card className="border-primary/20 shadow-md mb-2">
                <CardHeader className="bg-primary/5 rounded-t-lg">
                    <CardTitle className="flex items-center gap-2">
                        <Info className="h-5 w-5 text-primary" />
                        Overview
                    </CardTitle>
                    <CardDescription>General information about {supplement.name}</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="prose max-w-none">
                        <p>{supplement.description}</p>
                        <h3 className="font-medium mb-2 text-green-500">Health Benefits</h3>
                    <ul className="list-disc list-inside mb-4">
                        {supplement.scientificDetails.benefits?.map((benefit, index) => (
                            <li key={index}>{benefit}</li>
                        ))}
                    </ul>
                    <h3 className="font-medium mb-2 text-red-500">Side Effects</h3>
                    <ul className="list-disc list-inside">
                        {supplement.scientificDetails.sideEffects?.map((effect, index) => (
                            <li key={index}>{effect}</li>
                        ))}
                    </ul>
                    </div>
                </CardContent>
            </Card>

            <Tabs defaultValue="intake" className="w-full">
                <TabsList className="grid w-full grid-cols-3 bg-primary/5 border-primary/20 p-1 rounded-lg">
                    <TabsTrigger value="intake" className="data-[state=active]:bg-white">
                        <Clock className="h-4 w-4 mr-2 text-primary" />
                        Intake Practices
                    </TabsTrigger>
                    <TabsTrigger value="supplement-interactions" className="data-[state=active]:bg-white">
                        <AlertTriangle className="h-4 w-4 mr-2 text-primary" />
                        Supplement Interactions
                    </TabsTrigger>
                    <TabsTrigger value="food-interactions" className="data-[state=active]:bg-white">
                        <Utensils className="h-4 w-4 mr-2 text-primary" />
                        Food Interactions
                    </TabsTrigger>
                </TabsList>

                <TabsContent value="intake" className="mt-6">
                    <Card className="border-primary/20 shadow-md">
                        <CardHeader className="bg-primary/5 rounded-t-lg">
                            <CardTitle className="flex items-center gap-2">
                                <FileText className="h-5 w-5 text-primary" />
                                Best Intake Practices
                            </CardTitle>
                            <CardDescription>How to take {supplement.name} for optimal benefits</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6 pt-6">
                            <div>
                                <h3 className="font-medium mb-2 text-primary">Recommended Dosage</h3>
                                <p>{supplement.intakePractices.dosage}</p>
                            </div>
                            <div>
                                <h3 className="font-medium mb-2 text-primary">Timing</h3>
                                <p>{supplement.intakePractices.timing}</p>
                            </div>
                            <div>
                                <h3 className="font-medium mb-2 text-primary">Special Instructions</h3>
                                <p>{supplement.intakePractices.specialInstructions}</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Supplement Interactions */}
                <TabsContent value="supplement-interactions" className="mt-6">
                    <Card className="border-primary/20 shadow-md">
                        <CardHeader className="bg-primary/5 rounded-t-lg">
                            <CardTitle className="flex items-center gap-2">
                                <AlertTriangle className="h-5 w-5 text-primary" />
                                Supplement Interactions
                            </CardTitle>
                            <CardDescription>How {supplement.name} interacts with other supplements</CardDescription>
                        </CardHeader>
                        <CardContent className="pt-6">
                            {(interactions?.supplementSupplementInteractions ?? []).length > 0 ? (
                                <ul className="space-y-6">
                                    {interactions?.supplementSupplementInteractions.map((interaction, index) => (
                                        <li key={index} className="border-b pb-6 last:border-0 last:pb-0">
                                            <div className="flex items-start">
                                                <div className="mr-3">
                                                    <Badge
                                                        variant={
                                                            interaction.effect?.toLowerCase() === "negative"
                                                                ? "destructive"
                                                                : interaction.effect?.toLowerCase() === "positive"
                                                                    ? "default"
                                                                    : "secondary"
                                                        }
                                                        className={
                                                            interaction.effect?.toLowerCase() === "positive"
                                                                ? "bg-green-600"
                                                                : interaction.effect?.toLowerCase() === "negative"
                                                                    ? "bg-red-600"
                                                                    : ""
                                                        }
                                                    >
                                                        {interaction.effect
                                                            ? interaction.effect.charAt(0).toUpperCase() +
                                                            interaction.effect.slice(1)
                                                            : "Unknown"}
                                                    </Badge>
                                                </div>
                                                <div>
                                                    <h3 className="font-medium text-lg">
                                                        With{" "}
                                                        {interaction.supplements
                                                            .filter((s) => s.supplementId !== supplement._id)
                                                            .map((s) => s.name)
                                                            .join(", ")}
                                                    </h3>
                                        
                                                    {interaction.description && (
                                                        <p className="text-muted-foreground mt-2 mb-2">
                                                            {interaction.description}
                                                        </p>
                                                    )}
                                                    {interaction.recommendation && (
                                                        <div className="mt-2 bg-primary/5 p-3 rounded-md">
                                                            <p className="font-medium text-sm">Recommendation:</p>
                                                            <p className="text-sm">{interaction.recommendation}</p>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="text-center py-8 text-muted-foreground">
                                    <AlertTriangle className="h-10 w-10 mx-auto mb-3 opacity-30" />
                                    <p>No known supplement interactions for {supplement.name}.</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Food Interactions */}
                <TabsContent value="food-interactions" className="mt-6">
                    <Card className="border-primary/20 shadow-md">
                        <CardHeader className="bg-primary/5 rounded-t-lg">
                            <CardTitle className="flex items-center gap-2">
                                <Utensils className="h-5 w-5 text-primary" />
                                Food Interactions
                            </CardTitle>
                            <CardDescription>How {supplement.name} interacts with food</CardDescription>
                        </CardHeader>
                        <CardContent className="pt-6">
                            {(interactions?.supplementFoodInteractions?.length ?? 0) > 0 ? (
                                <ul className="space-y-6">
                                    {interactions?.supplementFoodInteractions.map((interaction, index) => (
                                        <li key={index} className="border-b pb-6 last:border-0 last:pb-0">
                                            <div className="flex items-start">
                                                <div className="mr-3">
                                                    <Badge
                                                        variant={
                                                            interaction.effect.includes("Positive")
                                                                ? "default"
                                                                : interaction.effect.includes("Negative")
                                                                    ? "destructive"
                                                                : "secondary"
                                                        }
                                                        className={
                                                            interaction.effect.includes("Positive")
                                                                ? "bg-green-600"
                                                                : interaction.effect.includes("Negative")
                                                                    ? "bg-red-600"
                                                                : ""
                                                        }
                                                    >
                                                        {interaction.effect}
                                                    </Badge>
                                                </div>
                                                <div>
                                                    <h3 className="font-medium text-lg">{interaction.foodItem || "Unknown Food"}</h3>
                                                    <p className="text-muted-foreground mt-2 mb-2">{interaction.description}</p>
                                                    {interaction.recommendation && (
                                                        <div className="mt-2 bg-primary/5 p-3 rounded-md">
                                                            <p className="font-medium text-sm">Recommendation:</p>
                                                            <p className="text-sm">{interaction.recommendation}</p>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="text-center py-8 text-muted-foreground">
                                    <Utensils className="h-10 w-10 mx-auto mb-3 opacity-30" />
                                    <p>No known food interactions for {supplement.name}.</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </PageContainer>
    )
}