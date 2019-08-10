﻿using NUnit.Framework;
using Scalar.FunctionalTests.FileSystemRunners;
using Scalar.Tests.Should;
using System.Collections.Generic;
using System.IO;

namespace Scalar.FunctionalTests.Tests.EnlistmentPerFixture
{
    [TestFixture]
    [Category(Categories.NeedsUpdatesForNonVirtualizedMode)]
    public class StatusVerbTests : TestsWithEnlistmentPerFixture
    {
        [TestCase]
        public void GitTrace()
        {
            Dictionary<string, string> environmentVariables = new Dictionary<string, string>();

            this.Enlistment.Status(trace: "1");
            this.Enlistment.Status(trace: "2");

            string logPath = Path.Combine(this.Enlistment.RepoRoot, "log-file.txt");
            this.Enlistment.Status(trace: logPath);

            FileSystemRunner fileSystem = new SystemIORunner();
            fileSystem.FileExists(logPath).ShouldBeTrue();
            string.IsNullOrWhiteSpace(fileSystem.ReadAllText(logPath)).ShouldBeFalse();
        }
    }
}
