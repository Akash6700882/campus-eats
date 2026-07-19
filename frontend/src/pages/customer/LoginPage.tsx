import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2, UtensilsCrossed } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/store/auth";
import { apiErrorMessage } from "@/lib/api";
import { authApi } from "@/api/auth";

const passwordSchema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
});
type PasswordForm = z.infer<typeof passwordSchema>;

const phoneSchema = z.object({
  phone: z.string().regex(/^\d{10}$/, "Enter a valid 10-digit phone number"),
});
type PhoneForm = z.infer<typeof phoneSchema>;

export function LoginPage() {
  const { login, loginWithOtp } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const redirectTo = (location.state as { from?: Location } | null)?.from?.pathname ?? "/";

  const [otpSent, setOtpSent] = useState(false);
  const [otpPhone, setOtpPhone] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [otpSubmitting, setOtpSubmitting] = useState(false);

  const passwordForm = useForm<PasswordForm>({ resolver: zodResolver(passwordSchema) });
  const phoneForm = useForm<PhoneForm>({ resolver: zodResolver(phoneSchema) });

  async function onPasswordSubmit(values: PasswordForm) {
    try {
      await login(values.email, values.password);
      toast.success("Welcome back!");
      navigate(redirectTo, { replace: true });
    } catch (err) {
      toast.error(apiErrorMessage(err, "Invalid email or password"));
    }
  }

  async function onRequestOtp(values: PhoneForm) {
    try {
      await authApi.requestOtp(values.phone);
      setOtpPhone(values.phone);
      setOtpSent(true);
      toast.success("OTP sent — check the backend console in dev mode");
    } catch (err) {
      toast.error(apiErrorMessage(err, "Could not send OTP"));
    }
  }

  async function onVerifyOtp() {
    setOtpSubmitting(true);
    try {
      await loginWithOtp(otpPhone, otpCode);
      toast.success("Welcome back!");
      navigate(redirectTo, { replace: true });
    } catch (err) {
      toast.error(apiErrorMessage(err, "Invalid or expired OTP"));
    } finally {
      setOtpSubmitting(false);
    }
  }

  return (
    <div className="container flex min-h-[calc(100vh-4rem)] max-w-md flex-col justify-center py-12">
      <div className="mb-6 flex flex-col items-center gap-2 text-center">
        <UtensilsCrossed className="h-8 w-8 text-primary" />
        <h1 className="font-heading text-2xl font-bold">Welcome back</h1>
        <p className="text-sm text-muted-foreground">Sign in to order from the campus canteen</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Sign in</CardTitle>
          <CardDescription>Use your password or a one-time code</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="password">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="password">Password</TabsTrigger>
              <TabsTrigger value="otp">OTP</TabsTrigger>
            </TabsList>

            <TabsContent value="password" className="mt-4">
              <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} className="space-y-4">
                <div className="space-y-1.5">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="you@campus.edu" {...passwordForm.register("email")} />
                  {passwordForm.formState.errors.email && (
                    <p className="text-xs text-destructive">{passwordForm.formState.errors.email.message}</p>
                  )}
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" type="password" {...passwordForm.register("password")} />
                  {passwordForm.formState.errors.password && (
                    <p className="text-xs text-destructive">{passwordForm.formState.errors.password.message}</p>
                  )}
                </div>
                <Button type="submit" className="w-full" disabled={passwordForm.formState.isSubmitting}>
                  {passwordForm.formState.isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
                  Sign in
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="otp" className="mt-4">
              {!otpSent ? (
                <form onSubmit={phoneForm.handleSubmit(onRequestOtp)} className="space-y-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="phone">Phone number</Label>
                    <Input id="phone" placeholder="9876543210" {...phoneForm.register("phone")} />
                    {phoneForm.formState.errors.phone && (
                      <p className="text-xs text-destructive">{phoneForm.formState.errors.phone.message}</p>
                    )}
                  </div>
                  <Button type="submit" className="w-full" disabled={phoneForm.formState.isSubmitting}>
                    {phoneForm.formState.isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
                    Send OTP
                  </Button>
                </form>
              ) : (
                <div className="space-y-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="otp">Enter the 6-digit code sent to {otpPhone}</Label>
                    <Input
                      id="otp"
                      inputMode="numeric"
                      maxLength={6}
                      value={otpCode}
                      onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ""))}
                    />
                  </div>
                  <Button className="w-full" disabled={otpCode.length !== 6 || otpSubmitting} onClick={onVerifyOtp}>
                    {otpSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
                    Verify & sign in
                  </Button>
                  <Button variant="ghost" className="w-full" onClick={() => setOtpSent(false)}>
                    Use a different number
                  </Button>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
        <CardFooter className="justify-center text-sm text-muted-foreground">
          New here?&nbsp;<Link to="/signup" className="font-medium text-primary hover:underline">Create an account</Link>
        </CardFooter>
      </Card>
    </div>
  );
}
