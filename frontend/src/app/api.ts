import { useToast } from '@/hooks/use-toast';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

interface Magazine {
  id: number;
  title: string;
  author: string;
  publication_date: string;
  category: string;
  content: string;
}

export const useLoadData = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  return useMutation({
    mutationKey: ['load'],
    mutationFn: async () => {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/load`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorMessage = await response.text();
        throw new Error(errorMessage || 'Failed to load data.');
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['search']);
      toast({
        title: 'Data loaded successfully!',
        description: 'Mockaroo data loaded and indexed.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to load data!',
        description: error.message || 'Unknown error occurred.',
        variant: 'destructive',
      });
    },
  }, queryClient);
};

export const useSearchData = (searchTerm: string, searchType: string) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  return useQuery<{ results: Magazine[] }>({
    queryKey: ['search', searchTerm, searchType],
    queryFn: async () => {
      if (searchTerm) {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/search?query=${searchTerm}&search_type=${searchType}`
        );
        if (!response.ok) {
          throw new Error('Failed to search data.');
        }
        return response.json();
      } else {
        return [];
      }
    },
    onSuccess: (data, variables, context) => {
      toast({
        title: 'Search successful!',
        description: 'Search results fetched successfully.',
      });
    },
    onError: (error, variables, context) => {
      toast({
        title: 'Search failed!',
        description: error.message,
        variant: 'destructive',
      });
    },
  }, queryClient);
};