# AI Employee File Processing Instructions

## Workflow for Needs_Action Folder

1. **Monitor** the `Needs_Action` folder for new `.md` files
2. **Parse** each file's YAML front matter to get:
   - Original file path
   - File size
   - Timestamp
3. **Locate** the original file using the path from metadata
4. **Process** the file according to its type (document, image, etc.)
5. **Move** processed files to `~/AI_Employee_Vault/Processed/`
6. **Delete** the `.md` marker file after successful processing
7. **Log** all actions with timestamps in `~/AI_Employee_Vault/audit.log`

## File Format Example
