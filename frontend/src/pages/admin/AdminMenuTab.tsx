import { useState } from "react";
import { Loader2, Plus, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useCategories, useFoods } from "@/hooks/useMenu";
import { useAdminMenuActions } from "@/hooks/useAdmin";
import { formatCurrency } from "@/lib/format";

export function AdminMenuTab() {
  const { data: categories, isLoading: categoriesLoading } = useCategories();
  const { data: foods, isLoading: foodsLoading } = useFoods({ limit: 200 });
  const { createCategory, deleteCategory, createFood, updateFood, deleteFood } = useAdminMenuActions();

  const [categoryName, setCategoryName] = useState("");
  const [foodName, setFoodName] = useState("");
  const [foodPrice, setFoodPrice] = useState("");
  const [foodCategoryId, setFoodCategoryId] = useState("");
  const [foodIsVeg, setFoodIsVeg] = useState(true);

  function handleAddCategory() {
    if (!categoryName.trim()) return;
    createCategory.mutate({ name: categoryName.trim() }, { onSuccess: () => setCategoryName("") });
  }

  function handleAddFood() {
    const price = Number(foodPrice);
    if (!foodName.trim() || !foodCategoryId || !price) return;
    createFood.mutate(
      { name: foodName.trim(), category_id: foodCategoryId, price, is_veg: foodIsVeg },
      {
        onSuccess: () => {
          setFoodName("");
          setFoodPrice("");
        },
      },
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <div>
        <h2 className="mb-3 font-heading text-lg font-semibold">Categories</h2>
        <Card className="mb-3">
          <CardContent className="flex items-end gap-2 py-4">
            <div className="flex-1 space-y-1.5">
              <Label htmlFor="category-name">New category</Label>
              <Input id="category-name" value={categoryName} onChange={(e) => setCategoryName(e.target.value)} placeholder="e.g. Desserts" />
            </div>
            <Button disabled={createCategory.isPending} onClick={handleAddCategory}>
              {createCategory.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
              Add
            </Button>
          </CardContent>
        </Card>

        {!categoriesLoading && (
          <div className="space-y-2">
            {categories?.map((category) => (
              <Card key={category.id}>
                <CardContent className="flex items-center justify-between py-2.5 text-sm">
                  <span>{category.name}</span>
                  <div className="flex items-center gap-2">
                    <Badge variant={category.is_active ? "default" : "outline"}>
                      {category.is_active ? "Active" : "Inactive"}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      className="text-muted-foreground hover:text-destructive"
                      onClick={() => deleteCategory.mutate(category.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      <div>
        <h2 className="mb-3 font-heading text-lg font-semibold">Food items</h2>
        <Card className="mb-3">
          <CardContent className="space-y-3 py-4">
            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1.5">
                <Label htmlFor="food-name">Name</Label>
                <Input id="food-name" value={foodName} onChange={(e) => setFoodName(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="food-price">Price (INR)</Label>
                <Input id="food-price" type="number" min="1" value={foodPrice} onChange={(e) => setFoodPrice(e.target.value)} />
              </div>
            </div>
            <div className="flex items-end gap-2">
              <div className="flex-1 space-y-1.5">
                <Label>Category</Label>
                <Select value={foodCategoryId} onValueChange={setFoodCategoryId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories?.map((c) => (
                      <SelectItem key={c.id} value={c.id}>
                        {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center gap-2 pb-2">
                <Switch checked={foodIsVeg} onCheckedChange={setFoodIsVeg} />
                <span className="text-sm">Veg</span>
              </div>
            </div>
            <Button className="w-full" disabled={createFood.isPending} onClick={handleAddFood}>
              {createFood.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Add food item
            </Button>
          </CardContent>
        </Card>

        {!foodsLoading && (
          <div className="max-h-[32rem] space-y-2 overflow-y-auto pr-1">
            {foods?.map((food) => (
              <Card key={food.id}>
                <CardContent className="flex items-center justify-between py-2.5 text-sm">
                  <div>
                    <p className="font-medium">{food.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {food.category_name} &middot; {formatCurrency(food.price)}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={food.is_available}
                      onCheckedChange={(checked) => updateFood.mutate({ id: food.id, payload: { is_available: checked } })}
                    />
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      className="text-muted-foreground hover:text-destructive"
                      onClick={() => deleteFood.mutate(food.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
