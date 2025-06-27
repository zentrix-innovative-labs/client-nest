# ClientNest Frontend Architecture

## Frontend Architecture Overview

ClientNest's frontend is built with **React 18** and follows a **component-driven architecture** with modern patterns:

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Zustand for global state, React Query for server state
- **Routing**: React Router v6 with nested routes
- **Deployment**: Vercel with automatic deployments

## Application Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND ARCHITECTURE                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Browser  │    │   CDN (Vercel)  │    │  Static Assets  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ React App       │────│ Edge Functions  │────│ Images, Fonts   │
│ Service Worker  │    │ Global Cache    │    │ Icons, Videos   │
│ Local Storage   │    │ SSL/HTTPS       │    │ Optimized Build │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            REACT APPLICATION                                   │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   App Shell     │   Route Layer   │  Component Tree │    State Management     │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ - Header        │ - Auth Routes   │ - Pages         │ - Zustand Stores        │
│ - Sidebar       │ - Dashboard     │ - Layouts       │ - React Query Cache     │
│ - Navigation    │ - Social Media  │ - Components    │ - Local State           │
│ - Footer        │ - AI Features   │ - UI Elements   │ - Form State            │
│ - Modals        │ - Settings      │ - Hooks         │ - Theme State           │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                         │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   HTTP Client   │   Auth Service  │  Error Handling │    Real-time Updates    │
├─────────────────┼─────────────────┼─────────────────┼─────────────────────────┤
│ - Axios Config  │ - JWT Tokens    │ - Error Boundary│ - WebSocket Client      │
│ - Interceptors  │ - Refresh Logic │ - Toast Messages│ - Server-Sent Events    │
│ - Request Queue │ - Route Guards  │ - Retry Logic   │ - Push Notifications    │
│ - Cache Control │ - Permissions   │ - Fallback UI   │ - Live Updates          │
└─────────────────┴─────────────────┴─────────────────┴─────────────────────────┘
```

## Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── ui/               # Basic UI elements
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   └── index.ts
│   ├── forms/            # Form components
│   │   ├── LoginForm.tsx
│   │   ├── PostForm.tsx
│   │   └── index.ts
│   ├── layout/           # Layout components
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Footer.tsx
│   │   └── index.ts
│   └── features/         # Feature-specific components
│       ├── auth/
│       ├── dashboard/
│       ├── social/
│       ├── ai/
│       └── analytics/
├── pages/                # Page components
│   ├── auth/
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   └── ForgotPasswordPage.tsx
│   ├── dashboard/
│   │   ├── DashboardPage.tsx
│   │   ├── OverviewPage.tsx
│   │   └── AnalyticsPage.tsx
│   ├── social/
│   │   ├── PostsPage.tsx
│   │   ├── CommentsPage.tsx
│   │   └── SchedulePage.tsx
│   └── settings/
│       ├── ProfilePage.tsx
│       ├── TeamPage.tsx
│       └── BillingPage.tsx
├── hooks/                # Custom React hooks
│   ├── useAuth.ts
│   ├── useApi.ts
│   ├── usePosts.ts
│   ├── useComments.ts
│   └── useAI.ts
├── stores/               # Zustand state stores
│   ├── authStore.ts
│   ├── uiStore.ts
│   ├── teamStore.ts
│   └── index.ts
├── services/             # API services
│   ├── api.ts
│   ├── auth.ts
│   ├── posts.ts
│   ├── comments.ts
│   ├── ai.ts
│   └── analytics.ts
├── utils/                # Utility functions
│   ├── constants.ts
│   ├── helpers.ts
│   ├── validation.ts
│   ├── formatting.ts
│   └── types.ts
├── styles/               # Global styles
│   ├── globals.css
│   ├── components.css
│   └── utilities.css
├── assets/               # Static assets
│   ├── images/
│   ├── icons/
│   └── fonts/
├── App.tsx               # Main app component
├── main.tsx              # App entry point
├── router.tsx            # Route configuration
└── vite-env.d.ts         # Vite type definitions
```

## Component Architecture

### Component Hierarchy

```
App
├── Router
│   ├── AuthLayout
│   │   ├── LoginPage
│   │   ├── RegisterPage
│   │   └── ForgotPasswordPage
│   └── DashboardLayout
│       ├── Header
│       │   ├── UserMenu
│       │   ├── TeamSelector
│       │   └── NotificationBell
│       ├── Sidebar
│       │   ├── Navigation
│       │   ├── QuickActions
│       │   └── AIUsageWidget
│       ├── MainContent
│       │   ├── DashboardPage
│       │   │   ├── StatsCards
│       │   │   ├── RecentPosts
│       │   │   ├── CommentsFeed
│       │   │   └── AIInsights
│       │   ├── PostsPage
│       │   │   ├── PostsList
│       │   │   ├── PostEditor
│       │   │   ├── MediaUploader
│       │   │   └── ScheduleCalendar
│       │   ├── CommentsPage
│       │   │   ├── CommentsList
│       │   │   ├── SentimentFilter
│       │   │   ├── ResponseEditor
│       │   │   └── AutoReplySettings
│       │   └── AnalyticsPage
│       │       ├── MetricsCharts
│       │       ├── PlatformBreakdown
│       │       ├── EngagementTrends
│       │       └── AIUsageStats
│       └── Footer
└── GlobalComponents
    ├── ErrorBoundary
    ├── LoadingSpinner
    ├── ToastContainer
    └── ModalProvider
```

### Component Design Patterns

#### 1. Compound Components

```tsx
// components/ui/Card.tsx
import React from 'react';
import { cn } from '@/utils/helpers';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

const Card = ({ children, className }: CardProps) => {
  return (
    <div className={cn(
      'rounded-lg border bg-card text-card-foreground shadow-sm',
      className
    )}>
      {children}
    </div>
  );
};

const CardHeader = ({ children, className }: CardHeaderProps) => {
  return (
    <div className={cn('flex flex-col space-y-1.5 p-6', className)}>
      {children}
    </div>
  );
};

const CardContent = ({ children, className }: CardContentProps) => {
  return (
    <div className={cn('p-6 pt-0', className)}>
      {children}
    </div>
  );
};

const CardFooter = ({ children, className }: CardFooterProps) => {
  return (
    <div className={cn('flex items-center p-6 pt-0', className)}>
      {children}
    </div>
  );
};

// Export compound component
Card.Header = CardHeader;
Card.Content = CardContent;
Card.Footer = CardFooter;

export { Card };

// Usage:
// <Card>
//   <Card.Header>
//     <h3>Title</h3>
//   </Card.Header>
//   <Card.Content>
//     <p>Content</p>
//   </Card.Content>
// </Card>
```

#### 2. Render Props Pattern

```tsx
// components/features/DataFetcher.tsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';

interface DataFetcherProps<T> {
  queryKey: string[];
  queryFn: () => Promise<T>;
  children: (data: {
    data: T | undefined;
    isLoading: boolean;
    error: Error | null;
    refetch: () => void;
  }) => React.ReactNode;
}

function DataFetcher<T>({ queryKey, queryFn, children }: DataFetcherProps<T>) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey,
    queryFn,
  });

  return (
    <>
      {children({ data, isLoading, error, refetch })}
    </>
  );
}

export { DataFetcher };

// Usage:
// <DataFetcher
//   queryKey={['posts']}
//   queryFn={fetchPosts}
// >
//   {({ data, isLoading, error }) => {
//     if (isLoading) return <LoadingSpinner />;
//     if (error) return <ErrorMessage error={error} />;
//     return <PostsList posts={data} />;
//   }}
// </DataFetcher>
```

#### 3. Higher-Order Components (HOCs)

```tsx
// components/hoc/withAuth.tsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';

interface WithAuthProps {
  requiredPermissions?: string[];
  redirectTo?: string;
}

function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options: WithAuthProps = {}
) {
  const { requiredPermissions = [], redirectTo = '/login' } = options;

  return function AuthenticatedComponent(props: P) {
    const { user, isAuthenticated, hasPermissions } = useAuthStore();

    if (!isAuthenticated) {
      return <Navigate to={redirectTo} replace />;
    }

    if (requiredPermissions.length > 0 && !hasPermissions(requiredPermissions)) {
      return <Navigate to="/unauthorized" replace />;
    }

    return <Component {...props} />;
  };
}

export { withAuth };

// Usage:
// const ProtectedDashboard = withAuth(DashboardPage, {
//   requiredPermissions: ['read:dashboard'],
//   redirectTo: '/login'
// });
```

## State Management

### Zustand Stores

#### Auth Store

```tsx
// stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '@/services/auth';

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  avatarUrl?: string;
  teams: Team[];
}

interface Team {
  id: string;
  name: string;
  role: string;
  planType: string;
}

interface AuthState {
  user: User | null;
  currentTeam: Team | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  setCurrentTeam: (team: Team) => void;
  updateProfile: (data: Partial<User>) => Promise<void>;
  hasPermissions: (permissions: string[]) => boolean;
}

const useAuthStore = create<AuthState>()(n  persist(
    (set, get) => ({
      user: null,
      currentTeam: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          const response = await authService.login(email, password);
          const { user, tokens } = response.data;
          
          // Store tokens
          localStorage.setItem('accessToken', tokens.access_token);
          localStorage.setItem('refreshToken', tokens.refresh_token);
          
          set({
            user,
            currentTeam: user.teams[0] || null,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (userData: RegisterData) => {
        set({ isLoading: true });
        try {
          const response = await authService.register(userData);
          const { user, tokens } = response.data;
          
          localStorage.setItem('accessToken', tokens.access_token);
          localStorage.setItem('refreshToken', tokens.refresh_token);
          
          set({
            user,
            currentTeam: user.teams[0] || null,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        set({
          user: null,
          currentTeam: null,
          isAuthenticated: false,
        });
      },

      refreshToken: async () => {
        try {
          const refreshToken = localStorage.getItem('refreshToken');
          if (!refreshToken) throw new Error('No refresh token');
          
          const response = await authService.refreshToken(refreshToken);
          const { access_token } = response.data;
          
          localStorage.setItem('accessToken', access_token);
        } catch (error) {
          get().logout();
          throw error;
        }
      },

      setCurrentTeam: (team: Team) => {
        set({ currentTeam: team });
      },

      updateProfile: async (data: Partial<User>) => {
        try {
          const response = await authService.updateProfile(data);
          const updatedUser = response.data;
          
          set(state => ({
            user: state.user ? { ...state.user, ...updatedUser } : null
          }));
        } catch (error) {
          throw error;
        }
      },

      hasPermissions: (permissions: string[]) => {
        const { currentTeam } = get();
        if (!currentTeam) return false;
        
        // Check if user has required permissions based on role
        const rolePermissions = getRolePermissions(currentTeam.role);
        return permissions.every(permission => 
          rolePermissions.includes(permission)
        );
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        currentTeam: state.currentTeam,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export { useAuthStore };
```

#### UI Store

```tsx
// stores/uiStore.ts
import { create } from 'zustand';

interface UIState {
  theme: 'light' | 'dark' | 'system';
  sidebarCollapsed: boolean;
  activeModal: string | null;
  notifications: Notification[];
  isLoading: boolean;
  
  // Actions
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  toggleSidebar: () => void;
  openModal: (modalId: string) => void;
  closeModal: () => void;
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  setLoading: (loading: boolean) => void;
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
}

const useUIStore = create<UIState>((set, get) => ({
  theme: 'system',
  sidebarCollapsed: false,
  activeModal: null,
  notifications: [],
  isLoading: false,

  setTheme: (theme) => {
    set({ theme });
    // Apply theme to document
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else if (theme === 'light') {
      document.documentElement.classList.remove('dark');
    } else {
      // System theme
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      document.documentElement.classList.toggle('dark', prefersDark);
    }
  },

  toggleSidebar: () => {
    set(state => ({ sidebarCollapsed: !state.sidebarCollapsed }));
  },

  openModal: (modalId) => {
    set({ activeModal: modalId });
  },

  closeModal: () => {
    set({ activeModal: null });
  },

  addNotification: (notification) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newNotification = { ...notification, id };
    
    set(state => ({
      notifications: [...state.notifications, newNotification]
    }));

    // Auto-remove notification after duration
    if (notification.duration !== 0) {
      setTimeout(() => {
        get().removeNotification(id);
      }, notification.duration || 5000);
    }
  },

  removeNotification: (id) => {
    set(state => ({
      notifications: state.notifications.filter(n => n.id !== id)
    }));
  },

  setLoading: (loading) => {
    set({ isLoading: loading });
  },
}));

export { useUIStore };
```

### React Query Integration

```tsx
// hooks/usePosts.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { postsService } from '@/services/posts';
import { useAuthStore } from '@/stores/authStore';
import { useUIStore } from '@/stores/uiStore';

interface Post {
  id: string;
  title: string;
  content: string;
  status: 'draft' | 'scheduled' | 'published' | 'failed';
  platforms: string[];
  scheduledAt?: string;
  publishedAt?: string;
  engagement: {
    likes: number;
    comments: number;
    shares: number;
    reach: number;
  };
}

interface CreatePostData {
  title: string;
  content: string;
  platforms: string[];
  scheduledAt?: string;
  mediaIds?: string[];
}

const usePosts = () => {
  const { currentTeam } = useAuthStore();
  const { addNotification } = useUIStore();
  const queryClient = useQueryClient();

  // Fetch posts
  const {
    data: posts,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['posts', currentTeam?.id],
    queryFn: () => postsService.getPosts(currentTeam?.id),
    enabled: !!currentTeam?.id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Create post mutation
  const createPostMutation = useMutation({
    mutationFn: (data: CreatePostData) => 
      postsService.createPost(currentTeam?.id, data),
    onSuccess: (newPost) => {
      // Update cache
      queryClient.setQueryData(
        ['posts', currentTeam?.id],
        (oldPosts: Post[] = []) => [newPost, ...oldPosts]
      );
      
      addNotification({
        type: 'success',
        title: 'Post Created',
        message: 'Your post has been created successfully',
      });
    },
    onError: (error) => {
      addNotification({
        type: 'error',
        title: 'Failed to Create Post',
        message: error.message,
      });
    },
  });

  // Update post mutation
  const updatePostMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreatePostData> }) =>
      postsService.updatePost(id, data),
    onSuccess: (updatedPost) => {
      // Update cache
      queryClient.setQueryData(
        ['posts', currentTeam?.id],
        (oldPosts: Post[] = []) =>
          oldPosts.map(post => 
            post.id === updatedPost.id ? updatedPost : post
          )
      );
      
      addNotification({
        type: 'success',
        title: 'Post Updated',
        message: 'Your post has been updated successfully',
      });
    },
  });

  // Delete post mutation
  const deletePostMutation = useMutation({
    mutationFn: (id: string) => postsService.deletePost(id),
    onSuccess: (_, deletedId) => {
      // Update cache
      queryClient.setQueryData(
        ['posts', currentTeam?.id],
        (oldPosts: Post[] = []) =>
          oldPosts.filter(post => post.id !== deletedId)
      );
      
      addNotification({
        type: 'success',
        title: 'Post Deleted',
        message: 'Your post has been deleted successfully',
      });
    },
  });

  return {
    posts,
    isLoading,
    error,
    refetch,
    createPost: createPostMutation.mutate,
    updatePost: updatePostMutation.mutate,
    deletePost: deletePostMutation.mutate,
    isCreating: createPostMutation.isPending,
    isUpdating: updatePostMutation.isPending,
    isDeleting: deletePostMutation.isPending,
  };
};

export { usePosts };
```

## Routing Architecture

### Route Configuration

```tsx
// router.tsx
import React from 'react';
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { AuthLayout } from '@/components/layout/AuthLayout';
import { DashboardLayout } from '@/components/layout/DashboardLayout';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

// Auth Pages
import { LoginPage } from '@/pages/auth/LoginPage';
import { RegisterPage } from '@/pages/auth/RegisterPage';
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage';

// Dashboard Pages
import { DashboardPage } from '@/pages/dashboard/DashboardPage';
import { PostsPage } from '@/pages/social/PostsPage';
import { CommentsPage } from '@/pages/social/CommentsPage';
import { AnalyticsPage } from '@/pages/analytics/AnalyticsPage';
import { SettingsPage } from '@/pages/settings/SettingsPage';

// Error Pages
import { NotFoundPage } from '@/pages/errors/NotFoundPage';
import { UnauthorizedPage } from '@/pages/errors/UnauthorizedPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    path: '/auth',
    element: <AuthLayout />,
    children: [
      {
        path: 'login',
        element: <LoginPage />,
      },
      {
        path: 'register',
        element: <RegisterPage />,
      },
      {
        path: 'forgot-password',
        element: <ForgotPasswordPage />,
      },
    ],
  },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DashboardLayout />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: 'posts',
        element: <PostsPage />,
      },
      {
        path: 'comments',
        element: <CommentsPage />,
      },
      {
        path: 'analytics',
        element: <AnalyticsPage />,
      },
      {
        path: 'settings',
        element: <SettingsPage />,
        children: [
          {
            path: 'profile',
            element: <ProfileSettingsPage />,
          },
          {
            path: 'team',
            element: <TeamSettingsPage />,
          },
          {
            path: 'billing',
            element: <BillingSettingsPage />,
          },
        ],
      },
    ],
  },
  {
    path: '/unauthorized',
    element: <UnauthorizedPage />,
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);

export { router };
```

### Protected Route Component

```tsx
// components/auth/ProtectedRoute.tsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermissions?: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermissions = [],
}) => {
  const { isAuthenticated, user, hasPermissions, isLoading } = useAuthStore();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <Navigate 
        to="/auth/login" 
        state={{ from: location.pathname }}
        replace 
      />
    );
  }

  if (requiredPermissions.length > 0 && !hasPermissions(requiredPermissions)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

export { ProtectedRoute };
```

## Performance Optimization

### Code Splitting

```tsx
// Lazy loading components
import { lazy, Suspense } from 'react';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

// Lazy load heavy components
const AnalyticsPage = lazy(() => import('@/pages/analytics/AnalyticsPage'));
const PostEditor = lazy(() => import('@/components/features/social/PostEditor'));
const MediaUploader = lazy(() => import('@/components/features/media/MediaUploader'));

// Wrapper component for lazy loading
const LazyComponent: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Suspense fallback={
    <div className="flex items-center justify-center p-8">
      <LoadingSpinner size="md" />
    </div>
  }>
    {children}
  </Suspense>
);

// Usage in routes
{
  path: 'analytics',
  element: (
    <LazyComponent>
      <AnalyticsPage />
    </LazyComponent>
  ),
}
```

### Memoization

```tsx
// components/features/social/PostsList.tsx
import React, { memo, useMemo } from 'react';
import { Post } from '@/types';

interface PostsListProps {
  posts: Post[];
  onEdit: (post: Post) => void;
  onDelete: (id: string) => void;
  filter: {
    status: string;
    platform: string;
    search: string;
  };
}

const PostsList = memo<PostsListProps>(({ posts, onEdit, onDelete, filter }) => {
  // Memoize filtered posts
  const filteredPosts = useMemo(() => {
    return posts.filter(post => {
      const matchesStatus = !filter.status || post.status === filter.status;
      const matchesPlatform = !filter.platform || 
        post.platforms.includes(filter.platform);
      const matchesSearch = !filter.search || 
        post.title.toLowerCase().includes(filter.search.toLowerCase()) ||
        post.content.toLowerCase().includes(filter.search.toLowerCase());
      
      return matchesStatus && matchesPlatform && matchesSearch;
    });
  }, [posts, filter]);

  // Memoize handlers
  const handleEdit = useMemo(() => {
    return (post: Post) => () => onEdit(post);
  }, [onEdit]);

  const handleDelete = useMemo(() => {
    return (id: string) => () => onDelete(id);
  }, [onDelete]);

  return (
    <div className="space-y-4">
      {filteredPosts.map(post => (
        <PostCard
          key={post.id}
          post={post}
          onEdit={handleEdit(post)}
          onDelete={handleDelete(post.id)}
        />
      ))}
    </div>
  );
});

PostsList.displayName = 'PostsList';

export { PostsList };
```

### Virtual Scrolling

```tsx
// components/ui/VirtualList.tsx
import React, { useMemo } from 'react';
import { FixedSizeList as List } from 'react-window';

interface VirtualListProps<T> {
  items: T[];
  height: number;
  itemHeight: number;
  renderItem: (props: { index: number; style: React.CSSProperties; data: T[] }) => React.ReactNode;
}

function VirtualList<T>({
  items,
  height,
  itemHeight,
  renderItem,
}: VirtualListProps<T>) {
  const ItemRenderer = useMemo(() => {
    return ({ index, style }: { index: number; style: React.CSSProperties }) => (
      <div style={style}>
        {renderItem({ index, style, data: items })}
      </div>
    );
  }, [items, renderItem]);

  return (
    <List
      height={height}
      itemCount={items.length}
      itemSize={itemHeight}
      itemData={items}
    >
      {ItemRenderer}
    </List>
  );
}

export { VirtualList };

// Usage for large comment lists
const CommentsList: React.FC<{ comments: Comment[] }> = ({ comments }) => {
  const renderComment = ({ index, style, data }: any) => (
    <div style={style} className="p-4 border-b">
      <CommentCard comment={data[index]} />
    </div>
  );

  return (
    <VirtualList
      items={comments}
      height={600}
      itemHeight={120}
      renderItem={renderComment}
    />
  );
};
```

## Error Handling

### Error Boundary

```tsx
// components/errors/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Button } from '@/components/ui/Button';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
    
    // Send error to monitoring service
    if (process.env.NODE_ENV === 'production') {
      // Example: Sentry.captureException(error);
    }
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: undefined });
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Something went wrong
            </h2>
            <p className="text-gray-600 mb-6">
              We're sorry, but something unexpected happened. Please try again.
            </p>
            <div className="space-x-4">
              <Button onClick={this.handleReset}>
                Try Again
              </Button>
              <Button 
                variant="outline" 
                onClick={() => window.location.reload()}
              >
                Reload Page
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export { ErrorBoundary };
```

### Global Error Handler

```tsx
// utils/errorHandler.ts
import { useUIStore } from '@/stores/uiStore';

interface ApiError {
  code: string;
  message: string;
  details?: any;
}

class ErrorHandler {
  private static instance: ErrorHandler;
  private addNotification: (notification: any) => void;

  constructor() {
    this.addNotification = useUIStore.getState().addNotification;
  }

  public static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  public handleApiError(error: any): void {
    const apiError: ApiError = error.response?.data?.error || {
      code: 'UNKNOWN_ERROR',
      message: 'An unexpected error occurred',
    };

    // Handle specific error codes
    switch (apiError.code) {
      case 'AUTH_001': // Invalid credentials
        this.addNotification({
          type: 'error',
          title: 'Authentication Failed',
          message: 'Invalid email or password',
        });
        break;

      case 'AUTH_002': // Token expired
        this.addNotification({
          type: 'warning',
          title: 'Session Expired',
          message: 'Please log in again',
        });
        // Redirect to login
        window.location.href = '/auth/login';
        break;

      case 'RATE_001': // Rate limit exceeded
        this.addNotification({
          type: 'warning',
          title: 'Rate Limit Exceeded',
          message: 'Please wait before making more requests',
        });
        break;

      case 'AI_001': // AI service unavailable
        this.addNotification({
          type: 'error',
          title: 'AI Service Unavailable',
          message: 'AI features are temporarily unavailable',
        });
        break;

      default:
        this.addNotification({
          type: 'error',
          title: 'Error',
          message: apiError.message,
        });
    }

    // Log error for debugging
    console.error('API Error:', apiError);
  }

  public handleNetworkError(): void {
    this.addNotification({
      type: 'error',
      title: 'Network Error',
      message: 'Please check your internet connection',
    });
  }

  public handleValidationError(errors: Record<string, string[]>): void {
    const firstError = Object.values(errors)[0]?.[0];
    if (firstError) {
      this.addNotification({
        type: 'error',
        title: 'Validation Error',
        message: firstError,
      });
    }
  }
}

export const errorHandler = ErrorHandler.getInstance();
```

## Testing Strategy

### Component Testing

```tsx
// __tests__/components/PostCard.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PostCard } from '@/components/features/social/PostCard';
import { Post } from '@/types';

const mockPost: Post = {
  id: '1',
  title: 'Test Post',
  content: 'This is a test post',
  status: 'published',
  platforms: ['facebook', 'instagram'],
  engagement: {
    likes: 10,
    comments: 5,
    shares: 2,
    reach: 100,
  },
  createdAt: '2024-01-15T10:00:00Z',
};

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('PostCard', () => {
  const mockOnEdit = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders post information correctly', () => {
    renderWithProviders(
      <PostCard 
        post={mockPost} 
        onEdit={mockOnEdit} 
        onDelete={mockOnDelete} 
      />
    );

    expect(screen.getByText('Test Post')).toBeInTheDocument();
    expect(screen.getByText('This is a test post')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument(); // likes
    expect(screen.getByText('5')).toBeInTheDocument(); // comments
  });

  it('calls onEdit when edit button is clicked', () => {
    renderWithProviders(
      <PostCard 
        post={mockPost} 
        onEdit={mockOnEdit} 
        onDelete={mockOnDelete} 
      />
    );

    const editButton = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editButton);

    expect(mockOnEdit).toHaveBeenCalledWith(mockPost);
  });

  it('calls onDelete when delete button is clicked', () => {
    renderWithProviders(
      <PostCard 
        post={mockPost} 
        onEdit={mockOnEdit} 
        onDelete={mockOnDelete} 
      />
    );

    const deleteButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);

    expect(mockOnDelete).toHaveBeenCalledWith(mockPost.id);
  });
});
```

### Hook Testing

```tsx
// __tests__/hooks/usePosts.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { usePosts } from '@/hooks/usePosts';
import { postsService } from '@/services/posts';

// Mock the posts service
jest.mock('@/services/posts');
const mockedPostsService = postsService as jest.Mocked<typeof postsService>;

// Mock auth store
jest.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    currentTeam: { id: 'team-1' },
  }),
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('usePosts', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('fetches posts successfully', async () => {
    const mockPosts = [
      { id: '1', title: 'Post 1', content: 'Content 1' },
      { id: '2', title: 'Post 2', content: 'Content 2' },
    ];

    mockedPostsService.getPosts.mockResolvedValue(mockPosts);

    const { result } = renderHook(() => usePosts(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.posts).toEqual(mockPosts);
    expect(mockedPostsService.getPosts).toHaveBeenCalledWith('team-1');
  });

  it('handles create post mutation', async () => {
    const newPost = { id: '3', title: 'New Post', content: 'New Content' };
    mockedPostsService.createPost.mockResolvedValue(newPost);

    const { result } = renderHook(() => usePosts(), {
      wrapper: createWrapper(),
    });

    const postData = {
      title: 'New Post',
      content: 'New Content',
      platforms: ['facebook'],
    };

    result.current.createPost(postData);

    await waitFor(() => {
      expect(result.current.isCreating).toBe(false);
    });

    expect(mockedPostsService.createPost).toHaveBeenCalledWith('team-1', postData);
  });
});
```

---

*This frontend architecture provides a solid foundation for ClientNest's React application, with modern patterns, performance optimizations, and comprehensive testing strategies.*