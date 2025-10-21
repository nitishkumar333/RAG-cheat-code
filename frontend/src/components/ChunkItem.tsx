import React, { useState } from 'react';
import type { LangchainDocument } from '../types';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Edit, Trash2, Save, X } from 'lucide-react';
import { Textarea } from './ui/Textarea';

interface ChunkItemProps {
  doc: LangchainDocument;
  onDelete: (id: string) => void;
  onUpdate: (id: string, newContent: string) => void;
}

export const ChunkItem: React.FC<ChunkItemProps> = ({ doc, onDelete, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(doc.page_content);

  const handleSave = () => {
    onUpdate(doc.id, editContent);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditContent(doc.page_content);
    setIsEditing(false);
  };

  return (
    <Card className="bg-secondary">
      <CardHeader>
        <CardTitle className="text-base font-medium">Chunk (Page {doc.metadata.page})</CardTitle>
        <CardDescription>Source: {doc.metadata.source}</CardDescription>
      </CardHeader>
      <CardContent>
        {isEditing ? (
          <Textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            rows={6}
            className="text-sm"
          />
        ) : (
          <p className="whitespace-pre-wrap text-sm text-muted-foreground">
            {doc.page_content}
          </p>
        )}
      </CardContent>
      <CardFooter className="flex justify-end gap-2">
        {isEditing ? (
          <>
            <Button variant="ghost" size="sm" onClick={handleCancel}>
              <X className="mr-1 h-4 w-4" /> Cancel
            </Button>
            <Button variant="default" size="sm" onClick={handleSave}>
              <Save className="mr-1 h-4 w-4" /> Save
            </Button>
          </>
        ) : (
          <>
            <Button variant="ghost" size="sm" onClick={() => setIsEditing(true)}>
              <Edit className="mr-1 h-4 w-4" /> Edit
            </Button>
            <Button variant="destructive" size="sm" onClick={() => onDelete(doc.id)}>
              <Trash2 className="mr-1 h-4 w-4" /> Delete
            </Button>
          </>
        )}
      </CardFooter>
    </Card>
  );
};