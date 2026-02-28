declare module "next/navigation" {
  export interface AppRouterInstance {
    replace(href: string, options?: { scroll?: boolean }): void;
  }

  export function useRouter(): AppRouterInstance;
  export function usePathname(): string;
  export function useSearchParams(): URLSearchParams;
}
