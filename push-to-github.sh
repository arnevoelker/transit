#!/bin/bash

echo "📦 Transit - Ready to push to GitHub!"
echo "===================================="
echo ""
echo "Please follow these steps:"
echo ""
echo "1. Go to https://github.com/new"
echo "2. Create a new repository named 'transit'"
echo "3. Make it PUBLIC"
echo "4. DO NOT initialize with README, .gitignore, or license"
echo "5. After creating, come back and press Enter to push"
echo ""
read -p "Press Enter when the repository is created..."

echo ""
echo "🚀 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Done! Your repository should now be live at:"
echo "   https://github.com/arnevoelker/transit"
echo ""
echo "Next steps:"
echo "- Add a LICENSE file (MIT or Apache 2.0 recommended)"
echo "- Create releases with git tags"
echo "- Add GitHub Actions for CI/CD"
echo "- Share with the community!"