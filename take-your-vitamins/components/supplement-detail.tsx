import type { Supplement } from "@/lib/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Clock, AlertTriangle, Utensils, ChevronLeft } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"


export function SupplementDetail({ supplement }: { supplement: Supplement }) {
    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold">{supplement.name}</h1>
                    <div className="flex items-center gap-2 mt-2">
                        <Badge variant="outline">{supplement.category}</Badge>
                        {supplement.aliases.length > 0 && (
                            <p className="text-sm text-muted-foreground">Also known as: {supplement.aliases.join(", ")}</p>
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

                <TabsContent value="supplement-interactions" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Supplement Interactions</CardTitle>
                            <CardDescription>How {supplement.name} interacts with other supplements</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {supplement.supplementInteractions.length > 0 ? (
                                <ul className="space-y-4">
                                    {supplement.supplementInteractions.map((interaction, index) => (
                                        <li key={index} className="border-b pb-4 last:border-0 last:pb-0">
                                            <div className="flex items-start">
                                                <div className="mr-2">
                                                    <Badge
                                                        variant={
                                                            interaction.severity === "high"
                                                                ? "destructive"
                                                                : interaction.severity === "medium"
                                                                    ? "warning"
                                                                    : "outline"
                                                        }
                                                    >
                                                        {interaction.severity.charAt(0).toUpperCase() + interaction.severity.slice(1)}
                                                    </Badge>
                                                </div>
                                                <div>
                                                    <h3 className="font-medium">With {interaction.supplementName}</h3>
                                                    <p>{interaction.effect}</p>
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

                <TabsContent value="food-interactions" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Food Interactions</CardTitle>
                            <CardDescription>How {supplement.name} interacts with food</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {supplement.foodInteractions.length > 0 ? (
                                <ul className="space-y-4">
                                    {supplement.foodInteractions.map((interaction, index) => (
                                        <li key={index} className="border-b pb-4 last:border-0 last:pb-0">
                                            <div className="flex items-start">
                                                <div className="mr-2">
                                                    <Badge
                                                        variant={
                                                            interaction.effect === "enhances absorption"
                                                                ? "success"
                                                                : interaction.effect === "reduces absorption"
                                                                    ? "destructive"
                                                                    : "outline"
                                                        }
                                                    >
                                                        {interaction.effect.includes("enhances")
                                                            ? "Enhances"
                                                            : interaction.effect.includes("reduces")
                                                                ? "Reduces"
                                                                : "Affects"}
                                                    </Badge>
                                                </div>
                                                <div>
                                                    <h3 className="font-medium">{interaction.foodName}</h3>
                                                    <p>{interaction.description}</p>
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
                                <p>No known food interactions for {supplement.name}.</p>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}

