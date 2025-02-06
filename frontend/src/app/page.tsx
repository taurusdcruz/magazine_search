'use client';

import React, { useState } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import Providers from './providers';
import { useLoadData, useSearchData } from './api';

interface Magazine {
  id: number;
  title: string;
  author: string;
  publication_date: string;
  category: string;
  content: string;
}

export default function Page() {
  return (
    <Providers>
      <Home />
    </Providers>
  );
}

function Home() {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [searchTermDebounced, setSearchTermDebounced] = useState<string>('');
  const [searchType, setSearchType] = useState<string>('hybrid');
  const [searchTypeDebounced, setSearchTypeDebounced] = useState<string>('hybrid');

  const { mutate: loadData } = useLoadData();
  const { data: searchResults, isLoading: isSearchLoading } = useSearchData(searchTermDebounced, searchTypeDebounced);
  return (
    <div className="container h-screen w-screen overflow-auto ">
      <div className="flex flex-col align-top items-start justify-start w-full p-10 gap-10">
        <Card className='w-full'>
          <CardHeader>
            <div className='flex align-middle items-center justify-center gap-10'>
              <Input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              <Select onValueChange={setSearchType} value={searchType}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select search type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="fulltext">Full-Text Search</SelectItem>
                  <SelectItem value="vector">Vector Search</SelectItem>
                  <SelectItem value="hybrid">Hybrid Search (RRF)</SelectItem>
                </SelectContent>
              </Select>
              <Button type="submit" onClick={() => {
                setSearchTermDebounced(searchTerm)
                setSearchTypeDebounced(searchType)
              }}>
                Search
              </Button>
              <Button onClick={() => loadData()} >Load Data</Button>
            </div>
          </CardHeader>
        </Card>
        {isSearchLoading ? (
          <div className="flex items-center justify-center w-full">
            <div className="w-10 h-10 border-t-2 border-b-2 border-gray-900 rounded-full animate-spin"></div>
          </div>
        ) : (
          <Results results={searchResults || []} />
        )}
      </div>
    </div>
  );
}


function Results({ results }: { results: Magazine }) {
  return (
    <div className="space-y-4 w-full">
      {(results || []).map((result, index) => (
        <React.Fragment key={index}>
          <Card>
            <CardHeader>
              <CardTitle>{result.title}</CardTitle>
              <CardDescription>
                by {result.author || 'Unknown Author'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea readOnly value={result.content || ''} />
            </CardContent>
          </Card>
          {index < results.length - 1 && <Separator />}
        </React.Fragment>
      ))}
    </div>
  );
}